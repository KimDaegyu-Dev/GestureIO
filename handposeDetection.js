import {
  createDetector,
  SupportedModels,
} from "@tensorflow-models/hand-pose-detection";
import * as tf from "@tensorflow/tfjs-node";
import cv from "opencv4nodejs";

async function main() {
  const model = SupportedModels.MediaPipeHands;
  const detectorConfig = {
    runtime: "tfjs", // Node.js에서는 'tfjs'를 사용합니다.
    modelType: "full",
  };
  const detector = await createDetector(model, detectorConfig);

  // 웹캠 설정
  const webcam = new cv.VideoCapture(0);
  webcam.set(cv.CAP_PROP_FRAME_WIDTH, 640);
  webcam.set(cv.CAP_PROP_FRAME_HEIGHT, 480);

  // 프레임을 캡처합니다.
  const frame = webcam.read();
  const image = cv.imencode(".jpg", frame).toString("base64");
  const buffer = Buffer.from(image, "base64");

  // 캡처한 이미지를 텐서로 변환합니다.
  const input = tf.node.decodeImage(buffer);

  // 손을 추정합니다.
  const hands = await detector.estimateHands(input);

  console.log(hands);
}

main().catch(console.error);
