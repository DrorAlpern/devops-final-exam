{{- define "monitor.name" -}}
{{- default .Release.Name .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "monitor.selectorLabels" -}}
app.kubernetes.io/name: flask-aws-monitor
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "monitor.labels" -}}
{{ include "monitor.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | quote }}
{{- end -}}
