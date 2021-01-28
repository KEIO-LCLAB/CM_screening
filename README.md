Cervical Myelopathy Screening
====
This page contains information about the screening software and program in the paper &quot;Cervical myelopathy screening with machine learning algorithm focusing on finger motion using non-contact sensor&quot;.

## Contents
- [Requirement](#requirement)
- [Quick Start OVerview](#quick-start-overview)
- [Parameter Set](#parameter-set)
- [How to make classification model](#how-to-make-classification-model)

## Requirement
- Leap Motion (Leap Motion, San Francisco, CA, USA)
- Unity
- Python3.6

## Quick Start Overview
You can execute our screening system easily if you can make new data.  
Install or copy &quot;CM_screening-main&quot; from the page top.  
We prepared a svm learning model &quot;svm_data.pkl&quot;, which is using a combination of parameters (the position and direction).

#### Unity Application (Get at least one person's data)
1. Prepare a computer with a macOS (Apple Inc., Cupertino, CA, USA) and Leap Motion.
2. Uncompress the compressed file &quot;HANZM_exe&quot;.
3. Open the folder &quot;HANZM_exe&quot; and start HANZM ver2.1.
4. Decide and input the 8-digit ID \*\*\*\*\*\*\*\* every each person.
5. Perform the examination by gripping and releasing fingers 20 times on the Leap Motion according to the Measurements in the paper.
6. Get the examination data at &quot;HANZM_exe/HANZM ver2.1/Contents/Log&quot;.

#### Python Software
7. Add the examination data from Unity into &quot;classification-data/\*\*\*\*\*\*\*\*&quot;(8-digit ID).  
   Please make a directory every user, which is named as &quot;\*\*\*\*\*\*\*\*&quot;(8-digit ID).
8. Execute cm_classification.py. After it, the classification result is shown.

## Parameter Set
Our data from Leap Motion has 35 features.  
- speed     : 0~4
- position  : 5~19
- direction : 20~34

## How to make classification model
You can make your svm learning model for classification.

#### Unity Application
Please get some people's data by [a similar flow](#unity-application-get-at-least-one-persons-data) .  

#### Python Software
7. Add the examination data from Unity into &quot;10s-test-data/Patient/\*\*\*\*\*\*\*\*&quot; or &quot;10s-test-data/Health/\*\*\*\*\*\*\*\*&quot;(8-digit ID).  
   Please make a directory every user, which is named as &quot;\*\*\*\*\*\*\*\*&quot;(8-digit ID).  
   If the data is CM patient's one, add into the former. If else, add into the latter.  
   ![Alt text](directory_path_image.PNG)
8. Execute make_model.py. After it, the classification result is shown.
