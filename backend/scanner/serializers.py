from rest_framework import serializers
from .models import Project, Scan, Vulnerability

class VulnerabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vulnerability
        fields = '__all__'

class ScanSerializer(serializers.ModelSerializer):
    vulnerabilities = VulnerabilitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Scan
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    scans = ScanSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
