from django.views import generic
from django.contrib.auth import logout, mixins, get_user_model
from django.urls import reverse_lazy
from django import http

from PIL import Image
import numpy as np

from . import forms

# TODO fix invalid form data leaking to template context in EditProfile
# TODO add in-ui image cropping and allow only square images

User = get_user_model()

HOMEPAGE = reverse_lazy("twitterx:home")

LOGIN_URL = reverse_lazy("users:login")

DEFAULT_PROFILE_PICTURE = "profile_pics/default.jpeg"


def squash_to_square(file):
	im = Image.open(file)
	sqrWidth = np.ceil(np.sqrt(im.size[0]*im.size[1])).astype(int)
	im_resize = im.resize((sqrWidth, sqrWidth))
	im_resize.save(file)


class ProfileView(generic.DetailView):
	template_name: str = "profiles/profile.html"
	model = User
	slug_field: str = "username"
	slug_url_kwarg: str = "username"


class EditProfile(mixins.LoginRequiredMixin, generic.UpdateView):
	template_name: str = "profiles/edit.html"
	fields = ["username", "email", "first_name", "last_name"]
	login_url = LOGIN_URL

	def get_object(self, queryset= None):
		return self.request.user


class DeleteProfile(mixins.LoginRequiredMixin, generic.DeleteView):
	template_name: str = "profiles/delete.html"
	model = User
	login_url = LOGIN_URL
	success_url = HOMEPAGE
	form_class = forms.ProfileDeleteForm

	def get_object(self, queryset= None):
		return self.request.user


	def get_form(self, form_class= None):
		form = super().get_form(form_class)
		form.expected = str(self.request.user)
		return form
	

	def form_valid(self, form):
		logout(self.request)
		return super().form_valid(form)


class FollowView(mixins.LoginRequiredMixin, generic.View):
	login_url = LOGIN_URL

	def post(self, request, *args, **kwargs):
		try:
			user = User.objects.get(username= kwargs["username"])
			if user == request.user:
				return http.HttpResponseBadRequest()

			if user in request.user.follows.all():
				request.user.follows.remove(user)
			else:
				request.user.follows.add(user)
			return http.HttpResponse(status= 204)
			
		except User.DoesNotExist:
			return http.HttpResponseBadRequest()


class EditPictureView(mixins.LoginRequiredMixin, generic.UpdateView):
	template_name: str = "profiles/picture.html"
	fields = ["profile_pic"]
	login_url = LOGIN_URL

	def get_object(self, queryset= None):
		return self.request.user

	
	def form_valid(self, form):
		ret = super().form_valid(form)
		squash_to_square(self.request.user.profile_pic.path)
		return ret


class DeletePictureView(mixins.LoginRequiredMixin, generic.View):
	login_url = LOGIN_URL

	def delete(self, request, *args, **kwargs):
		if request.user.profile_pic.name != DEFAULT_PROFILE_PICTURE:
			request.user.profile_pic.delete()
			request.user.profile_pic.name = DEFAULT_PROFILE_PICTURE
			request.user.save()
		return http.HttpResponseRedirect(request.user.get_absolute_url())

	post = delete