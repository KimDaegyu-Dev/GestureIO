import "@jxa/global-type";
import { run } from "@jxa/run";

/**
 * get safari version
 * This function execute JXA code
 */
export const UI = () => {
  return run(() => {
    const systemEvents = Application("System Events");
    const windows = systemEvents.processes["Music"].windows[0];
    windows.position = [100, 0];
    windows.size = [1000, 200];
    return windows.properties();
  });
};

/**
 * get current mac system user
 * This function execute JXA code
 */
export const frontMostApplication = () => {
  return run(() => {
    // System Events 애플리케이션 참조
    const systemEvents = Application("System Events");
    // 현재 포커스된 애플리케이션 식별
    const frontmostApp = systemEvents.processes.whose({ frontmost: true })[0];
    // 애플리케이션 이름 가져오기
    const appName = frontmostApp.name();
    console.log(`Frontmost Application: ${appName}`);

    // 맨 앞에 있는 창 확인
    const frontmostWindow = frontmostApp.windows[0];
    if (frontmostWindow) {
      const windowName = frontmostWindow.name();
      const windowPosition = frontmostWindow.position();
      const windowSize = frontmostWindow.size();
      let i = 100;
      for (i = 0; i < 1000; i++) {
        delay(0.1);
        frontmostWindow.position = [0 + i, 0];
      }
      frontmostWindow.size = [1300, 800];

      console.log(`Window Name: ${windowName}`);
      console.log(
        `Window Position: [${windowPosition[0]}, ${windowPosition[1]}]`
      );
      console.log(`Window Size: [${windowSize[0]}, ${windowSize[1]}]`);
    } else {
      console.log("No window found for the frontmost application.");
    }
  });
};

// This main is just a Node.js code
export const example = async () => {
  const version = await safariVersion();
  const userName = await currentUserName();
  return `User: ${userName}, Safari: ${version}`;
};

await frontMostApplication();
