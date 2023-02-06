from django.views import generic


class HomeView(generic.TemplateView):
	template_name: str = "twitterx/home.html"


class AboutView(generic.TemplateView):
	template_name: str = "twitterx/about.html"


class PrivacyPolicyView(generic.TemplateView):
	template_name: str = "twitterx/privacy.html"