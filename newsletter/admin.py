from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import NewsletterCategory, Subscriber, Subscription, Newsletter
from .tasks import send_newsletter_task

@admin.register(NewsletterCategory)
class NewsletterCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_default', 'is_active', 'created_date')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active', 'is_default')
    search_fields = ('name', 'description')

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'is_active', 'is_verified', 'subscribed_at')
    list_filter = ('is_active', 'is_verified', 'subscribed_at')
    search_fields = ('email', 'user__username')
    readonly_fields = ('unsubscribe_token',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'category', 'is_active', 'source', 'subscribed_at')
    list_filter = ('is_active', 'source', 'category')
    search_fields = ('subscriber__email',)

@admin.register(Newsletter)
class NewsletterAdmin(SummernoteModelAdmin):
    list_display = ('subject', 'status', 'created_date', 'sent_at')
    list_filter = ('status', 'created_date')
    search_fields = ('subject',)
    summernote_fields = ('content',)
    actions = ['send_newsletter']

    def send_newsletter(self, request, queryset):
        """Send selected newsletters via Celery task."""
        count = 0
        for newsletter in queryset:
            if newsletter.status == Newsletter.Status.SENT:
                self.message_user(request, f"Skipping '{newsletter.subject}': Already sent.", level='WARNING')
                continue
            
            send_newsletter_task.delay(newsletter.newsletter_id)
            count += 1
        
        if count > 0:
            self.message_user(request, f"Queued {count} newsletter(s) for sending.")
    
    send_newsletter.short_description = "Send selected newsletters"