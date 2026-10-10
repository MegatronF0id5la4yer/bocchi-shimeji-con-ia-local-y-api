package com.bocchi.pinkchan.shimeji;

import android.accessibilityservice.AccessibilityService;
import android.os.Build;
import android.view.accessibility.AccessibilityEvent;

public class JarvisAccessibilityService extends AccessibilityService {

    private static JarvisAccessibilityService instance;

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
    }

    @Override
    public void onDestroy() {
        if (instance == this) {
            instance = null;
        }
        super.onDestroy();
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        // No-op
    }

    @Override
    public void onInterrupt() {
        // No-op
    }

    public static boolean isAvailable() {
        return instance != null;
    }

    public static boolean takeScreenshot() {
        if (instance != null && Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            return instance.performGlobalAction(GLOBAL_ACTION_TAKE_SCREENSHOT);
        }
        return false;
    }

    public static boolean lockScreen() {
        if (instance != null && Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            return instance.performGlobalAction(GLOBAL_ACTION_LOCK_SCREEN);
        }
        return false;
    }
}

