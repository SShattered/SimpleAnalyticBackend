import cv2
import cupy as cp
import os
import threading
import socket
from Models import TaskModel
from ultralytics import YOLO
import base64

class Analytics(threading.Thread):

    target_width = 960
    target_height = 540
    model: YOLO
    taskModel: TaskModel
    video_path: str

    classIndex: int

    def __init__(self, task: TaskModel, client_socket: socket.socket, writeMessage):
        super().__init__()
        self.model = YOLO(f"D:\\SimpleAnalytic\\models\\{task.ModelType.lower()}{task.ModelVariation[0:1].lower()}.pt")
        self.model.to('cuda')
        self.video_path = task.InputURL
        self.taskModel = task
        self.classIndex = self.getDetectionIndex(task.Detection)
        self._stop_event = threading.Event()
        self.writeMessage = writeMessage
        self.client_socket = client_socket
        print(f"class detection: {self.classIndex} {task.Detection}")

    def stop(self):
        self._stop_event.set()
    
    def run(self):
        cap = cv2.VideoCapture(self.video_path)

        resize_interpolation = cv2.INTER_LINEAR

        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        #out = cv2.VideoWriter("D:\\data\\Output\\output.mp4", fourcc, 60, (self.target_width, self.target_height))

        frame_counter = 0
        # Loop through the video frames
        while not self._stop_event.is_set():
            # Read a frame from the video
            success, originalFrame1 = cap.read()

            #repeat
            frame_counter += 1
            if frame_counter == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                frame_counter = 0 #Or whatever as long as it is the same as next line
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            originalFrame = cv2.cvtColor(originalFrame1, cv2.COLOR_BGR2GRAY)
            originalFrame = cv2.cvtColor(originalFrame, cv2.COLOR_GRAY2BGR)

            # Upload frame to GPU
            gpu_frame = cv2.cuda.GpuMat()
            gpu_frame.upload(originalFrame)

            # Resize on GPU
            resized_gpu = cv2.cuda.resize(gpu_frame, (self.target_width, self.target_height), interpolation=resize_interpolation)

            # Download frame back to CPU
            frame = resized_gpu.download()

            if success:
                results = self.model.track(frame, persist=True)

                #scores = results[0].boxes.conf.numpy() # probabilities
                scores = cp.asnumpy(results[0].boxes.conf) # type: ignore
                #classes = results[0].boxes.cls.numpy() # predicted classes
                classes = cp.asnumpy(results[0].boxes.cls) # type: ignore
                #boxes = results[0].boxes.xyxy.numpy().astype(np.int32)
                boxer = cp.asnumpy(results[0].boxes.xyxy) # type: ignore
                boxes = boxer.astype(cp.int32)
                for score, cls, bbox in zip(scores, classes, boxes):
                    if int(cls) == self.classIndex:
                        cv2.rectangle(frame, (bbox[0], bbox[1]),
                                            (bbox[2], bbox[3]),
                                            color=(0, 0, 255),
                                            thickness=2)
                
                count = sum(1 for cls in classes if int(cls) == self.classIndex)
                        
                #out.write(frame)
                # Display the annotated frame
                #cv2.imshow(f"{self.taskModel.Id}", frame)

                _, img_encoded = cv2.imencode('.jpg', frame)
                data = img_encoded.tobytes()

                encoded_base64 = base64.b64encode(data)
                encoded_string = encoded_base64.decode("utf-8")
                self.writeMessage(self.taskModel.Id, self.client_socket, "Frame", encoded_string)
                self.writeMessage(self.taskModel.Id, self.client_socket, "Detections", str(count))

                # Break the loop if 'q' is pressed
                # if cv2.waitKey(1) & 0xFF == ord("q"):
                #     break
            else:
                # Break the loop if the end of the video is reached
                # video is repeated
                break

        # Release the video capture object and close the display window
        cap.release()
        #out.release()
        #cv2.destroyWindow(f"{self.taskModel.Id}")

    def getDetectionIndex(self, detection: str) -> int:
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "classes.txt")

            with open(file_path, "r") as file:
                lines = file.readlines()
                for index, line in enumerate(lines):
                    if detection in line.strip().lower():
                        return index
            return -1
        except Exception as e:
            print(e)
            return -1
