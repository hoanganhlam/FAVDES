from apps.trip.models import Schedule, Task, Discussion
from rest_framework import serializers
from apps.media.api.serializers import MediaSerializer
from apps.destination.api.serializers import DestinationSerializer
from apps.general.api.serializers import TaxonomySerializer


class ScheduleSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['id', 'title', 'note', 'tasks', 'media', 'destination_start', 'destination_end', 'taxonomies',
                  'user', 'options']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def to_representation(self, instance):
        self.fields['media'] = MediaSerializer(read_only=True)
        self.fields['destination_start'] = DestinationSerializer(read_only=True)
        self.fields['destination_end'] = DestinationSerializer(read_only=True)
        self.fields['taxonomies'] = TaxonomySerializer(many=True, read_only=True)
        return super(ScheduleSerializer, self).to_representation(instance)

    def get_tasks(self, instance):
        return TaskSerializer(instance.tasks, many=True).data


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def to_representation(self, instance):
        self.fields['destination'] = DestinationSerializer(read_only=True)
        return super(TaskSerializer, self).to_representation(instance)


class DiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def to_representation(self, instance):
        return super(DiscussionSerializer, self).to_representation(instance)
