
import cv2
import os
import face_recognition
import pickle


def detect_face_profile():
    print(os.getcwd())
    img = cv2.imread('./media/temp/temp.jpg')

    faceCascade = cv2.CascadeClassifier("./media/haarcascade_frontalface_alt.xml")

    # Read the image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    os.remove("./media/temp/temp.jpg")
    if len(faces) == 1:
        founded_faces = []
        
        try:
            f = open("model.sav", "rb")
            names, encoded_images = pickle.load(f)
            f.close()
        except:
            f = open("model.sav", "wb")
            pickle.dump(([], []),f)
            f.close()

            return False


        for (x, y, w, h) in faces:
            sub_face = img[y:y + h + 20, x:x + w + 20]
            cv2.cvtColor(sub_face, cv2.COLOR_BGR2RGB)
            sub_face = cv2.resize(sub_face, (0, 0), fx=0.25, fy=0.25)
            
            try:
                encodings = face_recognition.face_encodings(sub_face)[0]
            except:
                continue
            for img,n in zip(encoded_images,names):
                # match your image with the image and check if it matches
                result = face_recognition.compare_faces([encodings], img, tolerance=0.5)
                if result[0] == True:
                    return False





        return True
    else:
        return False


# detect_face_profile()

def face_tagging():
    founded_faces = []
    unfounded_faces = []
    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier("./media/haarcascade_frontalface_alt2.xml")

    f = open("model.sav", "rb")
    names, encoded_images = pickle.load(f)
    f.close()
    print(os.listdir("./media/security_picture/"))
    


    # Capture frame-by-frame
    frame = cv2.imread('./media/temp/temp.jpg')
    # cv2.imwrite("img.jpg",frame)
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
                #flags = cv2.CV_HAAR_SCALE_IMAGE
                )

    print("Found {0} faces!".format(len(faces)))

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        print(x,y,w,h)
        sub_face = frame[y:y + h + 20, x:x + w + 20]
        flag = False
        cv2.cvtColor(sub_face, cv2.COLOR_BGR2RGB)
        sub_face = cv2.resize(sub_face, (0, 0), fx=0.25, fy=0.25)
        # cv2.imwrite("cur.jpg",sub_face)
        try:
            encodings = face_recognition.face_encodings(sub_face)[0]
        except:
            #print("error")
            unfounded_faces.append([x,y,w,h])
            continue

        for img,n in zip(encoded_images,names):

            result = face_recognition.compare_faces([encodings], img, tolerance=0.5)
            if result[0] == True:
                # print("-"+img+"-")
                # print(n)
                founded_faces.append({"email":n.replace("__","@"),
                "x":x,"y":y,"w":w,"h":h})
                flag = True
                break
        if not flag:
            unfounded_faces.append([x,y,w,h])

    print(founded_faces)
    print(unfounded_faces)

    return founded_faces,unfounded_faces

def blur_face(path, faces):
    path = "."+path[6:]
    img = cv2.imread(path)

    for (x, y, w, h) in faces:
        blurImg = cv2.blur(img[y:y+h, x:x+w] ,(75,75))
        blurImg = cv2.GaussianBlur(blurImg, (5, 5), cv2.BORDER_DEFAULT)
        img[y:y+h, x:x+w] = blurImg
    cv2.imwrite(path, img)


def refresh_pickle():
    encoded_images = []
    names = []
    for i in os.listdir("./media/security_picture/"):
        loaded_image = face_recognition.load_image_file("./media/security_picture/"+i)
        print(loaded_image)
        print("./media/security_picture/"+i)
        encoded_image = face_recognition.face_encodings(loaded_image)[0]
        encoded_images.append(encoded_image)
        names.append(i[:-4])

    f = open("model.sav", "wb")
    pickle.dump((names, encoded_images),f)
    f.close()
