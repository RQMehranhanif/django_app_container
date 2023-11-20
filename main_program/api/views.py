from pyexpat.errors import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
# Create your views here.


# from mainprogram.functions.process_file import process_file

# Create your views here.
def index(request):
    return render(request, 'myuploadapp/index.html')
def hello_world(request):
    return render(request, 'myuploadapp/hello.html')
def service(request):
    return render(request, 'myuploadapp/service.html')
def about(request):
    return render(request, 'myuploadapp/contact.html')
def contact(request):
    return render(request, 'myuploadapp/hello.html')
# def excel_db(request):
#     if request.method == 'POST':
#         excel_file = request.FILES.get('excel_db_name')
#         # Provide default values for process_type and db_type
#         process_type = 'db'  # Adjust as needed
#         db_type = 'Local'
#             # Adjust as needed

#         try:
#             # Assuming process_file returns True on success, modify as needed
#             success = request.FILES['excel_db_name']
           
#             xlxs= process_file(success, process_type, db_type)
#             # breakpoint()
#             print(xlxs)
#             if xlxs:
#                 return HttpResponse("Congratulations! The process has been completed successfully.")
#             else:
#                 return HttpResponse("There was an error during the process.")
#         except Exception as e:
#                 # Print the exception for debugging
#                 print(f"Error in process_file: {e}")
#                 return HttpResponse("An unexpected error occurred during the process.")