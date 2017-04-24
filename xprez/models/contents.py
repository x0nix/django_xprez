# -*- coding: utf-8 -*-

from django.db import models
from django.template import Template, Context
from django.template.defaultfilters import striptags


from ..medium_editor.widgets import MediumEditorWidget
from ..medium_editor.utils import parse_text, render_text_parsed

from .base import Content, FormsetContent, AjaxUploadFormsetContent, ContentItem

from .. import contents_manager


class MediumEditor(Content):
    form_class = 'xprez.admin_forms.MediumEditorForm'
    admin_template_name = 'xprez/admin/contents/medium_editor.html'
    front_template_name = 'xprez/contents/medium_editor.html'
    icon_name = 'text_content'
    verbose_name = 'Text Content'

    text = models.TextField()
    css_class = models.CharField(max_length=100, null=True, blank=True)
    box = models.BooleanField(default=False)
    width = models.CharField(max_length=50, choices=Content.SIZE_CHOICES, default=Content.SIZE_FULL)

    class AdminMedia:
        js = MediumEditorWidget.Media.js
        css = MediumEditorWidget.Media.css['all']

    def show_front(self):
        return striptags(self.text) != ''

    def get_parsed_text(self):
        return parse_text(self.text)

    def render_text(self):
        return render_text_parsed(self.get_parsed_text())


class QuoteContent(FormsetContent):
    form_class = 'xprez.admin_forms.QuoteContentForm'
    formset_factory = 'xprez.admin_forms.QuoteFormSet'
    admin_template_name = 'xprez/admin/contents/quote.html'
    front_template_name = 'xprez/contents/quote.html'
    icon_name = 'quote'
    verbose_name = 'Quote'

    title = models.CharField(max_length=255, null=True, blank=True)
    box = models.BooleanField(default=False)

    display_two = models.BooleanField(default=False)

    def get_formset_queryset(self):
        return self.quotes.all()

    def show_front(self):
        quotes = self.quotes.all()
        if len(quotes) == 0:
            return False
        quote = quotes.first()
        if not quote.name or not quote.quote:
            return False
        return True


class Quote(ContentItem):
    content_foreign_key = 'content'
    content = models.ForeignKey(QuoteContent, related_name='quotes')
    name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='quotes', null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    quote = models.TextField()
    # position = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('content', 'id')


class Gallery(AjaxUploadFormsetContent):

    COLUMNS_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
    )

    form_class = 'xprez.admin_forms.GalleryForm'
    admin_template_name = 'xprez/admin/contents/gallery/gallery.html'
    admin_formset_item_template_name = 'xprez/admin/contents/gallery/photo.html'
    front_template_name = 'xprez/contents/gallery.html'
    icon_name = 'gallery'
    verbose_name = 'Gallery / Image'
    formset_factory = 'xprez.admin_forms.PhotoFormSet'

    width = models.CharField(max_length=50, choices=Content.SIZE_CHOICES, default=Content.SIZE_FULL)
    columns = models.PositiveSmallIntegerField(default=1)
    divided = models.BooleanField(default=False)
    crop = models.BooleanField(default=False)

    def get_formset_queryset(self):
        return self.photos.all()

    def save_admin_form(self):
        super(Gallery, self).save_admin_form()
        for index, photo in enumerate(self.photos.all()):
            photo.position = index
            photo.save()

    class FrontMedia:
        js = ('xprez/libs/photoswipe/dist/photoswipe.min.js', 'xprez/libs/photoswipe/dist/photoswipe-ui-default.min.js', 'xprez/js/photoswipe.js')
        css = ('xprez/libs/photoswipe/dist/photoswipe.css', 'xprez/libs/photoswipe/dist/default-skin/default-skin.css')

    def published_photos(self):
        return self.photos.all()

    def show_front(self):
        return self.photos.all().count()


class Photo(ContentItem):
    content_foreign_key = 'gallery'
    gallery = models.ForeignKey(Gallery, related_name='photos')
    image = models.ImageField(upload_to='photos')
    description = models.CharField(max_length=255, blank=True, null=True)
    position = models.PositiveSmallIntegerField()

    @classmethod
    def create_from_file(cls, django_file, gallery):
        photo = cls(gallery=gallery)
        photo.position = gallery.photos.all().count()
        photo.image.save(django_file.name.split("/")[-1], django_file)
        photo.save()
        return photo

    class Meta:
        ordering = ('position', )
        # unique_together = (
        #     ('gallery', 'position', )
        # )


class Video(Content):
    TYPE_CHOICES = {
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
    }
    admin_template_name = 'xprez/admin/contents/video.html'
    front_template_name = 'xprez/contents/video.html'
    verbose_name = 'Video'
    icon_name = 'video'
    form_class = 'xprez.admin_forms.VideoForm'

    poster_image = models.ImageField(upload_to='video', null=True, blank=True)
    url = models.URLField()
    width = models.CharField(max_length=50, choices=Content.SIZE_CHOICES, default=Content.SIZE_FULL)
    video_type = models.CharField(choices=TYPE_CHOICES, max_length=50)
    video_id = models.CharField(max_length=200)

    def save_admin_form(self):
        inst = self.admin_form.save(commit=False)
        inst.video_type = self.admin_form.video_type
        inst.video_id = self.admin_form.video_id
        inst.save()

    def show_front(self):
        return self.url

    class FrontMedia:
        js = ('xprez/js/video.js', 'xprez/libs/froogaloop/froogaloop.min.js',)


class CodeInput(Content):
    admin_template_name = 'xprez/admin/contents/code_input.html'
    front_template_name = 'xprez/contents/code_input.html'
    verbose_name = 'Code Input'
    icon_name = 'code'
    form_class = 'xprez.admin_forms.CodeInputForm'

    code = models.TextField()

    def show_front(self):
        return self.code


class NumbersContent(FormsetContent):
    admin_template_name = 'xprez/admin/contents/numbers.html'
    front_template_name = 'xprez/contents/numbers.html'
    verbose_name = 'Numbers'
    icon_name = 'numbers'
    form_class = 'xprez.admin_forms.NumbersContentForm'
    formset_factory = 'xprez.admin_forms.NumberFormSet'

    def get_formset_queryset(self):
        return self.numbers.all()

    def show_front(self):
        return self.numbers.all().count()

    class FrontMedia:
        js = ('xprez/libs/jquery.waypoints.min.js', 'xprez/libs/counter.up/jquery.counterup.js', 'xprez/js/numbers.js')


class Number(ContentItem):
    content_foreign_key = 'content'
    content = models.ForeignKey(NumbersContent, related_name='numbers')
    number = models.IntegerField(null=True, blank=True)
    suffix = models.CharField(max_length=10, null=True, blank=True)
    title = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ('content', 'id')


class FeatureBoxes(Content):
    admin_template_name = 'xprez/admin/contents/feature_boxes.html'
    front_template_name = 'xprez/contents/feature_boxes.html'
    verbose_name = 'Feature Boxes'
    icon_name = 'feature_boxes'
    form_class = 'xprez.admin_forms.FeatureBoxesForm'

    box_1 = models.TextField(blank=True)
    box_2 = models.TextField(blank=True)
    box_3 = models.TextField(blank=True)

    def show_front(self):
        return bool(self.box_1)


class CodeTemplate(Content):
    admin_template_name = 'xprez/admin/contents/code_template.html'
    verbose_name = 'Code Template'
    icon_name = 'code_template'
    form_class = 'xprez.admin_forms.CodeTemplateForm'

    template_name = models.CharField(max_length=255, null=True, blank=True)

    def show_front(self):
        return self.template_name

    def render_front(self):
        if self.show_front():
            try:
                with open(self.template_name, 'r') as my_file:
                    data = my_file.read()
                tpl = Template(data)
                ctx = Context({})
                return tpl.render(ctx)
            except IOError:
                return u'Invalid template: %s' % self.template_name
        else:
            return ''


class DownloadContent(AjaxUploadFormsetContent):
    admin_template_name = 'xprez/admin/contents/download/download.html'
    front_template_name = 'xprez/contents/download.html'
    admin_formset_item_template_name = 'xprez/admin/contents/download/attachment.html'

    verbose_name = 'Files'
    icon_name = 'files'
    form_class = 'xprez.admin_forms.DownloadContentForm'
    formset_factory = 'xprez.admin_forms.AttachmentFormSet'

    title = models.CharField(max_length=255, blank=True)

    def get_formset_queryset(self):
        return self.attachments.all()

    def show_front(self):
        return self.attachments.all().count()


class Attachment(ContentItem):
    content_foreign_key = 'content'
    content = models.ForeignKey(DownloadContent, related_name='attachments')
    file = models.FileField(upload_to='files')
    name = models.CharField(max_length=100, blank=True)
    position = models.PositiveSmallIntegerField()

    def get_name(self):
        return self.name or self.get_default_file_name()

    def get_extension(self):
        try:
            return self.file.name.split('/')[-1].split('.')[-1].lower()
        except (KeyError, IndexError):
            return ''

    def get_default_file_name(self):
        try:
            return self.file.name.split('/')[-1].split('.')[0]
        except (KeyError, IndexError):
            return 'unnamed'

    @classmethod
    def create_from_file(cls, django_file, content):
        att = cls(content=content)
        att.position = content.attachments.all().count()
        att.file.save(django_file.name.split("/")[-1], django_file)
        att.save()
        return att

    class Meta:
        ordering = ('position', )


contents_manager.register(MediumEditor)
contents_manager.register(QuoteContent)
contents_manager.register(Gallery)
contents_manager.register(DownloadContent)
contents_manager.register(Video)
contents_manager.register(NumbersContent)
contents_manager.register(FeatureBoxes)
contents_manager.register(CodeInput)
contents_manager.register(CodeTemplate)

















