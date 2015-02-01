import json
import os
import logging

from BeautifulSoup import BeautifulSoup
import pandas as pd

from django.conf import settings
from django.contrib.auth import authenticate, logout as auth_logout, login
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import View

from app.forms import ExtendedUserForm, UserFilesForm
from app.models import UserFiles

logger = logging.getLogger(__name__)


class LoginRequiredMixinRedirect(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixinRedirect, cls).as_view(**initkwargs)
        return login_required(login_url="/app/login/")(view)


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required()(view)


class Login(View):

    def get(self, request):
        if request.user.is_authenticated():
            return redirect('app:home')
        else:
            return render(request, 'login.html')


class ClassicLogin(View):

    def post(self, request):
        map = {False: 'un', True: ''}
        logger.info('Login request received from an {}autenticated user.'.format(map[request.user.is_authenticated()]))

        if not request.user.is_authenticated():
            email = request.POST['email']
            password = request.POST['password']
            logger.info('Email: {} | Password: {}'.format(email, password))
            user = authenticate(email=email, password=password)
            if user is not None:
                logger.info('User authenticated successfully. Redirect to home page.')
                login(request, user)
                return redirect('app:home')
            else:
                logger.info('Failed to authenticate user. Redirect to login page.')
                return redirect('app:login')
        else:
            logger.info('Redirected user to logn page.')
            return redirect('app:login')


class ClassicSignUP(View):

    def post(self, request):

        logger.info('Classic signup request recived with info: {}'.format(request.POST))
        if not request.user.is_authenticated():
            logger.info('Signup request is not from an already logged in user.')
            form = ExtendedUserForm(request.POST)
            if form.is_valid():
                logger.info('Signup request data is valid.')
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                logger.info('User created successfully with id:{}.'.format(user.id))
                login(request,
                      authenticate(email=user.email,
                                   password=form.cleaned_data['password']))
                return redirect('app:home')
            else:
                logger.error('Invalid form data, redirect log login page.')
                return redirect('app:login')
        else:
            logger.error('An already logged in user sent a signup request.')
            return redirect('app:home')


class Logout(View):
    def get(self, request):
        if request.user.is_authenticated():
            auth_logout(request)
            logger.info('User {} logged out successfully.'.format(request.user.id))
            return redirect('app:login')
        else:
            logger.info('User should be logged in to send a logout request.'.format(request.user.id))
            return redirect('app:login')


class Home(LoginRequiredMixinRedirect, View):

    def get(self, request):
        split_filename = os.path.split
        logger.info('Home view request from user {}.'.format(request.user.id))
        queryset = UserFiles.objects.filter(userid=request.user).order_by('-upload_time')
        old_files = queryset.values('actual_name', 'uploaded_file')
        for file in old_files:
            file['uploaded_file'] = split_filename(file['uploaded_file'])[-1]
        try:
            logger.info('Check if user already uploaded something, if yes read the latest file.')
            file = queryset[0]
            try:
                p = pd.read_csv(os.path.join(settings.MEDIA_ROOT, file.uploaded_file.name))
                p = p.where((pd.notnull(p)), None)
                headers = list(p.columns.values)
                data = p.to_dict('records')
                _, saved_name = split_filename(file.uploaded_file.name)
                logger.info("User's latest file was {}, now returning its data on the "
                            "home page.".format(saved_name))
                return render(request, 'home.html', {'headers': headers,
                                                     'data': json.dumps(data),
                                                     'file_name': saved_name,
                                                     'old_files': old_files})
            except pd.parser.CParserError:
                logger.error('File found in db but pandas failed to oarse it due to incorrect format.')
                return render(request, 'home.html')
        except IndexError:
            logger.error('User {} has not uploaded any file yet.'.format(request.user.id))
            return render(request, 'home.html')


class File_upload(LoginRequiredMixin, View):

    def post(self, request):

        form = UserFilesForm(request.POST, request.FILES)
        logger.info('Received a file upload request with POST data: {} and '
                    'FILES data: {} from user: {}'.format(request.POST, request.FILES, request.user.id))

        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.actual_name = form.cleaned_data['uploaded_file'].name
            uploaded_file.save()
            _, saved_name = os.path.split(uploaded_file.uploaded_file.name)
            logger.info("Form was fine. File {} with actual name is saved as {}.".format(uploaded_file.actual_name,
                                                                                         saved_name))

            try:
                form.cleaned_data['uploaded_file'].seek(0)
                logger.info('Pass the file path to pandas.read_csv()')
                p = pd.read_csv(form.cleaned_data['uploaded_file'])
                p = p.where((pd.notnull(p)), None)
            except pd.parser.CParserError:
                logger.error('Failed to read the file, file is not in proper format.')
                uploaded_file.delete()
                return HttpResponse(json.dumps({'status': False, 'error': 'Incorrect file format.'}),
                                    content_type='applications/json',
                                    status=400)
            else:
                logger.info('File read successfully.')
                return HttpResponse(json.dumps({'status': True,
                                                'headers': list(p.columns.values),
                                                'data': p.to_dict('records'),
                                                'file_name': saved_name
                                                }),
                                    content_type='applications/json')
        else:
            logger.error('Form was not not fine, errors: {}'.format(form.errors))
            return HttpResponse(json.dumps(dict(form.errors, **{'status': False})),
                                content_type='applications/json',
                                status=400)


class Cross_tabulate(LoginRequiredMixin, View):

    def post(self, request):
        file_name = os.path.join('files', request.POST['file_name'])
        field1 = request.POST['field1']
        field2 = request.POST['field2']
        logger.info('Cross tabulation request received with fields {}, {} for file by '
                    'user {}.'.format(field1, field2, request.POST['file_name'], request.user.id))

        try:
            logger.info('Looking for the file in database.')
            file = request.user.files.get(uploaded_file=file_name)
        except UserFiles.DoesNotExist:
            logger.error('File {} not found'.format(file_name))
            return HttpResponse(json.dumps({'status': False, 'error': 'No such file found.'}),
                                content_type='application/json', status=400)
        else:
            logger.info('File found, time to read it and cross-tabulate on the columns passed.')
            try:
                p = pd.read_csv(os.path.join(settings.MEDIA_ROOT, file.uploaded_file.name))
                p = p.where((pd.notnull(p)), None)
                html = p.pivot_table(index=[field1, field2], aggfunc=[len]).to_html()
                soup = BeautifulSoup(html)
                soup.table['class'] = "table table-bordered"
                # Remove unwanted rows from the generated table.
                for tr in soup.thead.findAll('tr')[:1]:
                    tr.replaceWith('')
                # soup.tr.findAll('th')[-1].string = 'Count'
                logger.info('File cross-tabulated successfully.')
                return HttpResponse(json.dumps({'data': str(soup), 'status': True}), content_type='application/json')
            except Exception as e:
                logger.error('An error occured while processing the file for cross-tabulation: {}'.format(e))
                return HttpResponse(json.dumps({'status': False, 'error': str(e)}),
                                    content_type='application/json', status=400)


class Load_old_file(LoginRequiredMixin, View):

    def post(self, request):

        file_name = os.path.join('files', request.POST['file_name'])
        logger.info('Received a request to load en existing file {!r} from user {}'.format(file_name,
                                                                                           request.user.id))
        try:
            logger.info('Looking for the file {!r} in database.'.format(file_name))
            file = request.user.files.get(uploaded_file=file_name)
        except UserFiles.DoesNotExist:
            logger.error('File {!r} not found in database.'.format(file_name))
            return HttpResponse(json.dumps({'status': False, 'error': 'No such file found.'}),
                                content_type='application/json', status=400)
        else:
            logger.info('File found, time to process it using pandas.read_csv()')
            try:
                p = pd.read_csv(os.path.join(settings.MEDIA_ROOT, file.uploaded_file.name))
                p = p.where((pd.notnull(p)), None)
                logger.info('File read successfully, returning the data to user.')
                return HttpResponse(json.dumps({'status': True,
                                                'headers': list(p.columns.values),
                                                'data': p.to_dict('records'),
                                                'file_name': request.POST['file_name']
                                                }),
                                    content_type='applications/json')
            except pd.parser.CParserError:
                logger.error('Failed to read the file, file is not in proper format.')
                return HttpResponse(json.dumps({'status': False, 'error': 'Incorrect file format.'}),
                                    content_type='application/json', status=400)
