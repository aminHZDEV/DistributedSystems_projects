from rest_framework.decorators import api_view
from rest_framework.response import Response
from kubernetes import client, config


@api_view(["GET"])
def get_instance_kuber_id(request):
    print(request.path)
    if request.method == "GET" and request.path == "/instance_id/":
        try:
            config.load_incluster_config()  # Load the current pod's in-cluster configuration
            # Get the current pod's metadata
            pod_name = config.load_incluster_config().pod_name
            pod_id = config.load_incluster_config().pod_id

            return Response({"pod_name": pod_name, "pod_id": pod_id})
        except Exception as e:
            print("error found pod id : ", e)
            return Response({"message": "pod not found"}, status=404)
    else:
        return Response({"message": "Invalid request"}, status=400)
