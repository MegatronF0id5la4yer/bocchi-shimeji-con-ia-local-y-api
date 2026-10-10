package com.bocchi.pinkchan.shimeji;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import android.database.Cursor;
import android.provider.OpenableColumns;
import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import org.json.JSONArray;
import org.json.JSONObject;

public class MainActivity extends Activity {

    private static final int REQUEST_OVERLAY_PERMISSION = 2001;
    private static final int REQUEST_RECORD_AUDIO_PERMISSION = 2002;
    private static final int REQUEST_PICK_SKIN_ZIP = 2048;

    public static final String PREFS_NAME = "pinkchan_shimeji_prefs";
    public static final String KEY_SKIN = "selected_skin";
    public static final String KEY_SIZE = "selected_size";
    public static final String KEY_ZERO_G = "zero_gravity";
    public static final String KEY_ACCENT_INDEX = "selected_accent_index";

    public static final String ACTION_OPEN_CHAT = "com.bocchi.pinkchan.shimeji.OPEN_CHAT";
    public static final String KEY_ALLOWED_APPS = "allowed_launch_packages";
    public static final String KEY_BUBBLE_ALPHA = "bubble_alpha";
    public static final String KEY_BUBBLE_BORDER = "bubble_border";
    public static final String KEY_LAST_UPDATE_CHECK = "last_update_check_time";
    private static final long UPDATE_CHECK_INTERVAL_MS = 2 * 24 * 60 * 60 * 1000L;

    public static final String KEY_AI_MODE = "ai_mode";
    public static final String KEY_GEMINI_KEY = "gemini_api_key";
    public static final String KEY_GEMINI_MODEL = "gemini_model";
    public static final String KEY_CLOUD_ENDPOINT = "cloud_endpoint";
    public static final String KEY_CLOUD_MODEL = "cloud_model";
    public static final String KEY_CLOUD_KEY = "cloud_api_key";
    public static final String KEY_CUSTOM_SLOTS = "custom_command_slots";


    // Header & Badges
    private TextView tvAppTitle;
    private TextView badgePremium;

    // 4 Screens & Tabs
    private TextView tabFeatured, tabInstalled, tabInspector, tabSettings;
    private View screenFeatured, screenInstalled, screenInspector, screenSettings;
    private int currentTabIndex = 0;
    private int currentAccentColor = 0;

    // Screen 1: Featured
    private TextView btnGridCompact, btnGridStandard, btnGridWide;
    private TextView tvActiveOverlayCount;
    private Button btnSpawnKonata, btnSpawnBocchi, btnSpawnMonika, btnSpawnNatsuki, btnSpawnSayori, btnSpawnYuri;
    private Button btnSpawnHachi, btnSpawnUsagi, btnSpawnPusheen;
    private View cardCharKonata, cardCharBocchi, cardCharMonika, cardCharNatsuki, cardCharSayori, cardCharYuri;
    private View cardCharHachi, cardCharUsagi, cardCharPusheen;

    // Screen 2: Installed
    private View btnActionImport, btnActionGuide;
    private Button btnListSpawnKonata, btnListSpawnBocchi, btnListSpawnMonika;
    private Button btnListSpawnNatsuki, btnListSpawnSayori, btnListSpawnYuri, btnListSpawnHachi, btnListSpawnUsagi, btnListSpawnPusheen;
    private Button btnAddCategories;

    // Screen 3: Inspector
    private TextView tvInspectorStatus;
    private ImageView ivInspectorMascot;
    private Button btnSpawnCustom, btnInteractionButton, btnCustomizeViews, btnInspectorChat, btnInspectorVoice;
    private Button btnInspectorGuitar, btnInspectorBox, btnInspectorCenter;
    private Button btnInspectorPlay, btnInspectorDance, btnInspectorTermux, btnInspectorFiles;

    // Screen 4: Settings
    private TextView badgeSizeNum;
    private RadioGroup rgSettingsSize;
    private Button btnCustomSize;
    private CheckBox cbSettingsZeroG;
    private SeekBar sbBubbleAlpha;
    private TextView badgeBubbleAlpha;
    private CheckBox cbBubbleBorder;
    private Button btnSettingsPermission;
    private Button btnSettingsAppFilter;
    private Button btnSettingsClearExtras;
    private Button btnSettingsStop;
    private Button btnSettingsCheckUpdate;
    private TextView tvUpdateInfo;

    // AI Engine Views
    private RadioGroup rgAiMode;
    private RadioButton rbAiLocal, rbAiGemini, rbAiCloud;
    private View layoutGeminiConfig, layoutCloudConfig;
    private EditText etGeminiKey, etGeminiModel;
    private EditText etCloudEndpoint, etCloudModel, etCloudKey;
    private Button btnTestAi, btnSaveAi;
    private TextView tvAiStatus;
    private SeekBar sbAiMaxTokens;
    private TextView tvAiMaxTokensVal;
    private Button btnImportSkinZip;
    private Button btnLoadPrebuiltMacros;

    // Prefabricated Command Slots Views
    private TextView badgeSlotsCount, tvEmptySlots;
    private LinearLayout layoutSlotsContainer;
    private Button btnAddCommandSlot;

    // JARVIS Agent Views
    private EditText etJarvisName, etJarvisPrompt, etJarvisWakePhrase;
    private CheckBox cbJarvisUseSkin, cbPermApps, cbPermSystem, cbPermReminders, cbPermFilesWrite, cbPermFilesDelete, cbPermShell;
    private CheckBox cbJarvisTts, cbJarvisWakeWord, cbChatPosLocked;
    private CheckBox cbAllowWallClimb, cbAllowCeiling, cbAllowSitting, cbAllowCustomActions;
    private SeekBar sbJarvisSteps, sbTtsRate, sbTtsPitch, sbShimejiSpeed, sbShimejiGravity, sbShimejiTalk;
    private TextView badgeJarvisSteps, tvTtsRateVal, tvTtsPitchVal, tvShimejiSpeedVal, tvShimejiGravityVal, tvShimejiTalkVal;
    private Button btnJarvisAccessibility, btnJarvisTestTts, btnJarvisPushToTalk, btnAddJarvisMacro, btnSaveJarvisAll;
    private LinearLayout layoutMacrosContainer;

    private SharedPreferences prefs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);

        initViews();
        setupTabs();
        setupFeaturedScreen();
        setupInstalledScreen();
        setupInspectorScreen();
        setupSettingsScreen();
        restoreSavedPreferences();

        handleIntent(getIntent());
        checkForUpdates(false);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleIntent(intent);
    }

    private void handleIntent(Intent intent) {
        if (intent != null && ACTION_OPEN_CHAT.equals(intent.getAction())) {
            showChatDialog();
        }
    }

    private void initViews() {
        tabFeatured = findViewById(R.id.tab_featured);
        tabInstalled = findViewById(R.id.tab_installed);
        tabInspector = findViewById(R.id.tab_inspector);
        tabSettings = findViewById(R.id.tab_settings);

        screenFeatured = findViewById(R.id.screen_featured);
        screenInstalled = findViewById(R.id.screen_installed);
        screenInspector = findViewById(R.id.screen_inspector);
        screenSettings = findViewById(R.id.screen_settings);

        tvAppTitle = findViewById(R.id.tv_app_title);
        badgePremium = findViewById(R.id.badge_premium);

        // Featured views
        tvActiveOverlayCount = findViewById(R.id.tv_active_overlay_count);
        btnGridCompact = findViewById(R.id.btn_grid_compact);
        btnGridStandard = findViewById(R.id.btn_grid_standard);
        btnGridWide = findViewById(R.id.btn_grid_wide);

        cardCharKonata = findViewById(R.id.card_char_konata);
        cardCharBocchi = findViewById(R.id.card_char_bocchi);
        cardCharMonika = findViewById(R.id.card_char_monika);
        cardCharNatsuki = findViewById(R.id.card_char_natsuki);
        cardCharSayori = findViewById(R.id.card_char_sayori);
        cardCharYuri = findViewById(R.id.card_char_yuri);
        cardCharHachi = findViewById(R.id.card_char_hachi);
        cardCharUsagi = findViewById(R.id.card_char_usagi);
        cardCharPusheen = findViewById(R.id.card_char_pusheen);

        btnSpawnKonata = findViewById(R.id.btn_spawn_konata);
        btnSpawnBocchi = findViewById(R.id.btn_spawn_bocchi);
        btnSpawnMonika = findViewById(R.id.btn_spawn_monika);
        btnSpawnNatsuki = findViewById(R.id.btn_spawn_natsuki);
        btnSpawnSayori = findViewById(R.id.btn_spawn_sayori);
        btnSpawnYuri = findViewById(R.id.btn_spawn_yuri);
        btnSpawnHachi = findViewById(R.id.btn_spawn_hachi);
        btnSpawnUsagi = findViewById(R.id.btn_spawn_usagi);
        btnSpawnPusheen = findViewById(R.id.btn_spawn_pusheen);

        // Installed views
        btnActionImport = findViewById(R.id.btn_action_import);
        btnActionGuide = findViewById(R.id.btn_action_guide);
        btnListSpawnKonata = findViewById(R.id.btn_list_spawn_konata);
        btnListSpawnBocchi = findViewById(R.id.btn_list_spawn_bocchi);
        btnListSpawnMonika = findViewById(R.id.btn_list_spawn_monika);
        btnListSpawnNatsuki = findViewById(R.id.btn_list_spawn_natsuki);
        btnListSpawnSayori = findViewById(R.id.btn_list_spawn_sayori);
        btnListSpawnYuri = findViewById(R.id.btn_list_spawn_yuri);
        btnListSpawnHachi = findViewById(R.id.btn_list_spawn_hachi);
        btnListSpawnUsagi = findViewById(R.id.btn_list_spawn_usagi);
        btnListSpawnPusheen = findViewById(R.id.btn_list_spawn_pusheen);
        btnAddCategories = findViewById(R.id.btn_add_categories);

        // Inspector views
        tvInspectorStatus = findViewById(R.id.tv_inspector_status);
        ivInspectorMascot = findViewById(R.id.iv_inspector_mascot);
        btnSpawnCustom = findViewById(R.id.btn_spawn_custom);
        btnInteractionButton = findViewById(R.id.btn_interaction_button);
        btnCustomizeViews = findViewById(R.id.btn_customize_views);
        btnInspectorChat = findViewById(R.id.btn_inspector_chat);
        btnInspectorVoice = findViewById(R.id.btn_inspector_voice);
        btnInspectorGuitar = findViewById(R.id.btn_inspector_guitar);
        btnInspectorBox = findViewById(R.id.btn_inspector_box);
        btnInspectorCenter = findViewById(R.id.btn_inspector_center);
        btnInspectorPlay = findViewById(R.id.btn_inspector_play);
        btnInspectorDance = findViewById(R.id.btn_inspector_dance);
        btnInspectorTermux = findViewById(R.id.btn_inspector_termux);
        btnInspectorFiles = findViewById(R.id.btn_inspector_files);

        // Settings views
        badgeSizeNum = findViewById(R.id.badge_size_num);
        rgSettingsSize = findViewById(R.id.rg_settings_size);
        btnCustomSize = findViewById(R.id.btn_custom_size);
        cbSettingsZeroG = findViewById(R.id.cb_settings_zerog);
        sbBubbleAlpha = findViewById(R.id.sb_bubble_alpha);
        badgeBubbleAlpha = findViewById(R.id.badge_bubble_alpha);
        cbBubbleBorder = findViewById(R.id.cb_bubble_border);
        btnSettingsPermission = findViewById(R.id.btn_settings_permission);
        btnSettingsAppFilter = findViewById(R.id.btn_settings_app_filter);
        btnSettingsClearExtras = findViewById(R.id.btn_settings_clear_extras);
        btnSettingsStop = findViewById(R.id.btn_settings_stop);
        btnSettingsCheckUpdate = findViewById(R.id.btn_settings_check_update);
        tvUpdateInfo = findViewById(R.id.tv_update_info);

        // AI Engine Views
        rgAiMode = findViewById(R.id.rg_ai_mode);
        rbAiLocal = findViewById(R.id.rb_ai_local);
        rbAiGemini = findViewById(R.id.rb_ai_gemini);
        rbAiCloud = findViewById(R.id.rb_ai_cloud);
        layoutGeminiConfig = findViewById(R.id.layout_gemini_config);
        layoutCloudConfig = findViewById(R.id.layout_cloud_config);
        etGeminiKey = findViewById(R.id.et_gemini_key);
        etGeminiModel = findViewById(R.id.et_gemini_model);
        etCloudEndpoint = findViewById(R.id.et_cloud_endpoint);
        etCloudModel = findViewById(R.id.et_cloud_model);
        etCloudKey = findViewById(R.id.et_cloud_key);
        btnTestAi = findViewById(R.id.btn_test_ai);
        btnSaveAi = findViewById(R.id.btn_save_ai);
        tvAiStatus = findViewById(R.id.tv_ai_status);

        // Prefabricated Command Slots Views
        badgeSlotsCount = findViewById(R.id.badge_slots_count);
        tvEmptySlots = findViewById(R.id.tv_empty_slots);
        layoutSlotsContainer = findViewById(R.id.layout_slots_container);
        btnAddCommandSlot = findViewById(R.id.btn_add_command_slot);

        // JARVIS Agent Views
        etJarvisName = findViewById(R.id.et_jarvis_name);
        etJarvisPrompt = findViewById(R.id.et_jarvis_prompt);
        etJarvisWakePhrase = findViewById(R.id.et_jarvis_wake_phrase);
        cbJarvisUseSkin = findViewById(R.id.cb_jarvis_use_skin);
        cbPermApps = findViewById(R.id.cb_perm_apps);
        cbPermSystem = findViewById(R.id.cb_perm_system);
        cbPermReminders = findViewById(R.id.cb_perm_reminders);
        cbPermFilesWrite = findViewById(R.id.cb_perm_files_write);
        cbPermFilesDelete = findViewById(R.id.cb_perm_files_delete);
        cbPermShell = findViewById(R.id.cb_perm_shell);
        cbJarvisTts = findViewById(R.id.cb_jarvis_tts);
        cbJarvisWakeWord = findViewById(R.id.cb_jarvis_wake_word);
        cbChatPosLocked = findViewById(R.id.cb_chat_pos_locked);
        cbAllowWallClimb = findViewById(R.id.cb_allow_wall_climb);
        cbAllowCeiling = findViewById(R.id.cb_allow_ceiling);
        cbAllowSitting = findViewById(R.id.cb_allow_sitting);
        cbAllowCustomActions = findViewById(R.id.cb_allow_custom_actions);
        sbJarvisSteps = findViewById(R.id.sb_jarvis_steps);
        sbTtsRate = findViewById(R.id.sb_tts_rate);
        sbTtsPitch = findViewById(R.id.sb_tts_pitch);
        sbShimejiSpeed = findViewById(R.id.sb_shimeji_speed);
        sbShimejiGravity = findViewById(R.id.sb_shimeji_gravity);
        sbShimejiTalk = findViewById(R.id.sb_shimeji_talk);
        badgeJarvisSteps = findViewById(R.id.badge_jarvis_steps);
        tvTtsRateVal = findViewById(R.id.tv_tts_rate_val);
        tvTtsPitchVal = findViewById(R.id.tv_tts_pitch_val);
        tvShimejiSpeedVal = findViewById(R.id.tv_shimeji_speed_val);
        tvShimejiGravityVal = findViewById(R.id.tv_shimeji_gravity_val);
        tvShimejiTalkVal = findViewById(R.id.tv_shimeji_talk_val);
        btnJarvisAccessibility = findViewById(R.id.btn_jarvis_accessibility);
        btnJarvisTestTts = findViewById(R.id.btn_jarvis_test_tts);
        btnJarvisPushToTalk = findViewById(R.id.btn_jarvis_push_to_talk);
        btnAddJarvisMacro = findViewById(R.id.btn_add_jarvis_macro);
        btnLoadPrebuiltMacros = findViewById(R.id.btn_load_prebuilt_macros);
        btnSaveJarvisAll = findViewById(R.id.btn_save_jarvis_all);
        layoutMacrosContainer = findViewById(R.id.layout_macros_container);
        btnImportSkinZip = findViewById(R.id.btn_import_skin_zip);
        sbAiMaxTokens = findViewById(R.id.sb_ai_max_tokens);
        tvAiMaxTokensVal = findViewById(R.id.tv_ai_max_tokens_val);
    }

    private void setupTabs() {
        tabFeatured.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectTab(0);
            }
        });

        tabInstalled.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectTab(1);
            }
        });

        tabInspector.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectTab(2);
            }
        });

        tabSettings.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectTab(3);
            }
        });
    }

    private void selectTab(int index) {
        currentTabIndex = index;
        int activeColor = (currentAccentColor != 0)
            ? currentAccentColor
            : getResources().getColor(R.color.accent_lavender_light);
        int inactiveColor = getResources().getColor(R.color.text_secondary);

        tabFeatured.setBackgroundResource(index == 0 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        tabFeatured.setTextColor(index == 0 ? activeColor : inactiveColor);

        tabInstalled.setBackgroundResource(index == 1 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        tabInstalled.setTextColor(index == 1 ? activeColor : inactiveColor);

        tabInspector.setBackgroundResource(index == 2 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        tabInspector.setTextColor(index == 2 ? activeColor : inactiveColor);

        tabSettings.setBackgroundResource(index == 3 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        tabSettings.setTextColor(index == 3 ? activeColor : inactiveColor);

        screenFeatured.setVisibility(index == 0 ? View.VISIBLE : View.GONE);
        screenInstalled.setVisibility(index == 1 ? View.VISIBLE : View.GONE);
        screenInspector.setVisibility(index == 2 ? View.VISIBLE : View.GONE);
        screenSettings.setVisibility(index == 3 ? View.VISIBLE : View.GONE);
    }

    private void setupFeaturedScreen() {
        btnGridCompact.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setGridSizeTab(0);
            }
        });
        btnGridStandard.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setGridSizeTab(1);
            }
        });
        btnGridWide.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setGridSizeTab(2);
            }
        });

        // Spawn & Card click handlers for all 9 characters
        View.OnClickListener clickKonata = new View.OnClickListener() {
            @Override public void onClick(View v) { spawnOrSelectSkin("Konata"); }
        };
        btnSpawnKonata.setOnClickListener(clickKonata);
        if (cardCharKonata != null) cardCharKonata.setOnClickListener(clickKonata);

        View.OnClickListener clickBocchi = new View.OnClickListener() {
            @Override public void onClick(View v) { spawnOrSelectSkin("Bocchi"); }
        };
        btnSpawnBocchi.setOnClickListener(clickBocchi);
        if (cardCharBocchi != null) cardCharBocchi.setOnClickListener(clickBocchi);

        View.OnClickListener clickMonika = new View.OnClickListener() {
            @Override public void onClick(View v) { spawnOrSelectSkin("Monika"); }
        };
        btnSpawnMonika.setOnClickListener(clickMonika);
        if (cardCharMonika != null) cardCharMonika.setOnClickListener(clickMonika);

        View.OnClickListener clickNatsuki = new View.OnClickListener() {
            @Override public void onClick(View v) { spawnOrSelectSkin("Natsuki"); }
        };
        btnSpawnNatsuki.setOnClickListener(clickNatsuki);
        if (cardCharNatsuki != null) cardCharNatsuki.setOnClickListener(clickNatsuki);

        View.OnClickListener clickSayori = new View.OnClickListener() {
            @Override public void onClick(View v) { spawnOrSelectSkin("Sayori"); }
        };
        btnSpawnSayori.setOnClickListener(clickSayori);
        if (cardCharSayori != null) cardCharSayori.setOnClickListener(clickSayori);

        View.OnClickListener clickYuri = new View.OnClickListener() {
            @Override public void onClick(View v) { spawnOrSelectSkin("Yuri"); }
        };
        btnSpawnYuri.setOnClickListener(clickYuri);
        if (cardCharYuri != null) cardCharYuri.setOnClickListener(clickYuri);

        View.OnClickListener clickHachi = new View.OnClickListener() {
            @Override public void onClick(View v) { spawnOrSelectSkin("Hachi"); }
        };
        btnSpawnHachi.setOnClickListener(clickHachi);
        if (cardCharHachi != null) cardCharHachi.setOnClickListener(clickHachi);

        View.OnClickListener clickUsagi = new View.OnClickListener() {
            @Override public void onClick(View v) { spawnOrSelectSkin("Usagi"); }
        };
        btnSpawnUsagi.setOnClickListener(clickUsagi);
        if (cardCharUsagi != null) cardCharUsagi.setOnClickListener(clickUsagi);

        View.OnClickListener clickPusheen = new View.OnClickListener() {
            @Override public void onClick(View v) { spawnOrSelectSkin("Pusheen"); }
        };
        btnSpawnPusheen.setOnClickListener(clickPusheen);
        if (cardCharPusheen != null) cardCharPusheen.setOnClickListener(clickPusheen);
    }

    private void setGridSizeTab(int idx) {
        int activeColor = (currentAccentColor != 0)
            ? currentAccentColor
            : getResources().getColor(R.color.accent_lavender_light);
        int inactiveColor = getResources().getColor(R.color.text_secondary);

        btnGridCompact.setBackgroundResource(idx == 0 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        btnGridCompact.setTextColor(idx == 0 ? activeColor : inactiveColor);

        btnGridStandard.setBackgroundResource(idx == 1 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        btnGridStandard.setTextColor(idx == 1 ? activeColor : inactiveColor);

        btnGridWide.setBackgroundResource(idx == 2 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        btnGridWide.setTextColor(idx == 2 ? activeColor : inactiveColor);
    }

    private void setupInstalledScreen() {
        btnActionImport.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(MainActivity.this, "Importar Shimeji: Carpeta de assets/skins lista", Toast.LENGTH_SHORT).show();
            }
        });

        btnActionGuide.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(MainActivity.this, "Guia: Usa frames PNG de 128x128 píxeles", Toast.LENGTH_LONG).show();
            }
        });

        btnListSpawnKonata.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Konata");
            }
        });

        btnListSpawnBocchi.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Bocchi");
            }
        });

        btnListSpawnMonika.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Monika");
            }
        });

        btnListSpawnNatsuki.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Natsuki");
            }
        });

        btnListSpawnSayori.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Sayori");
            }
        });

        btnListSpawnYuri.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Yuri");
            }
        });

        btnListSpawnHachi.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Hachi");
            }
        });

        btnListSpawnUsagi.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Usagi");
            }
        });

        btnListSpawnPusheen.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Pusheen");
            }
        });

        btnAddCategories.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(MainActivity.this, "Nueva categoria personalizada anadida", Toast.LENGTH_SHORT).show();
            }
        });

        if (btnImportSkinZip != null) {
            btnImportSkinZip.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                    intent.setType("*/*");
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                    startActivityForResult(Intent.createChooser(intent, "Seleccionar archivo ZIP de Skin"), REQUEST_PICK_SKIN_ZIP);
                }
            });
        }
    }

    private void setupInspectorScreen() {
        btnSpawnCustom.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (ShimejiService.isRunning) {
                    Intent intent = new Intent(MainActivity.this, ShimejiService.class);
                    intent.setAction(ShimejiService.ACTION_ADD_SHIMEJI);
                    startService(intent);
                } else {
                    String savedSkin = prefs.getString(KEY_SKIN, "Konata");
                    startShimejiWithSkin(savedSkin);
                }
            }
        });

        btnInteractionButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (ShimejiService.isRunning) {
                    Intent it = new Intent(MainActivity.this, ShimejiService.class);
                    it.setAction(ShimejiService.ACTION_DROP_ITEM);
                    startService(it);
                    Toast.makeText(MainActivity.this, "Soltando item para el Shimeji!", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(MainActivity.this, "Inicia el Shimeji para soltar items.", Toast.LENGTH_SHORT).show();
                }
            }
        });

        btnCustomizeViews.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerAction("cycle_skin");
            }
        });

        if (btnInspectorChat != null) {
            btnInspectorChat.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showChatDialog();
                }
            });
        }

        btnInspectorVoice.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!ShimejiService.isRunning) {
                    startShimejiWithSkin("Konata");
                }
                checkAndStartVoiceAssistant();
            }
        });

        btnInspectorGuitar.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerAction("guitar");
            }
        });

        btnInspectorBox.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerAction("box");
            }
        });

        btnInspectorCenter.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (ShimejiService.isRunning) {
                    Intent intent = new Intent(MainActivity.this, ShimejiService.class);
                    intent.setAction(ShimejiService.ACTION_CENTER);
                    startService(intent);
                } else {
                    Toast.makeText(MainActivity.this, "Inicia el Shimeji primero", Toast.LENGTH_SHORT).show();
                }
            }
        });

        btnInspectorPlay.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerAction("play");
            }
        });

        btnInspectorDance.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerAction("dance");
            }
        });

        btnInspectorTermux.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                launchTermux();
            }
        });

        btnInspectorFiles.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                createDemoFilesAndFolders();
            }
        });
    }

    private void setupSettingsScreen() {
        rgSettingsSize.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(RadioGroup group, int checkedId) {
                int sizeDp = 128;
                if (checkedId == R.id.rb_size_96) sizeDp = 96;
                else if (checkedId == R.id.rb_size_160) sizeDp = 160;

                badgeSizeNum.setText(sizeDp + " dp");
                prefs.edit().putInt(KEY_SIZE, sizeDp).apply();

                if (ShimejiService.isRunning) {
                    Intent intent = new Intent(MainActivity.this, ShimejiService.class);
                    intent.setAction(ShimejiService.ACTION_SET_SIZE);
                    intent.putExtra(ShimejiService.EXTRA_SIZE_DP, sizeDp);
                    startService(intent);
                }
            }
        });

        if (btnCustomSize != null) {
            btnCustomSize.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showCustomSizeDialog();
                }
            });
        }

        cbSettingsZeroG.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                prefs.edit().putBoolean(KEY_ZERO_G, isChecked).apply();

                if (ShimejiService.isRunning) {
                    Intent intent = new Intent(MainActivity.this, ShimejiService.class);
                    intent.setAction(ShimejiService.ACTION_SET_GRAVITY);
                    intent.putExtra(ShimejiService.EXTRA_ZERO_GRAVITY, isChecked);
                    startService(intent);
                }
            }
        });

        if (sbBubbleAlpha != null) {
            sbBubbleAlpha.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                @Override
                public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                    int clamped = Math.max(10, progress);
                    if (badgeBubbleAlpha != null) {
                        badgeBubbleAlpha.setText(clamped + "% Opacidad");
                    }
                    prefs.edit().putInt(KEY_BUBBLE_ALPHA, clamped).apply();
                    if (ShimejiService.isRunning) {
                        Intent it = new Intent(MainActivity.this, ShimejiService.class);
                        it.setAction(ShimejiService.ACTION_SET_BUBBLE);
                        startService(it);
                    }
                }
                @Override public void onStartTrackingTouch(SeekBar seekBar) {}
                @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            });
        }

        if (cbBubbleBorder != null) {
            cbBubbleBorder.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
                @Override
                public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                    prefs.edit().putBoolean(KEY_BUBBLE_BORDER, isChecked).apply();
                    if (ShimejiService.isRunning) {
                        Intent it = new Intent(MainActivity.this, ShimejiService.class);
                        it.setAction(ShimejiService.ACTION_SET_BUBBLE);
                        startService(it);
                    }
                }
            });
        }

        btnSettingsPermission.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                requestOverlayPermission();
            }
        });

        btnSettingsAppFilter.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showAppFilterDialog();
            }
        });

        if (btnSettingsCheckUpdate != null) {
            btnSettingsCheckUpdate.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    checkForUpdates(true);
                }
            });
        }

        btnSettingsClearExtras.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (ShimejiService.isRunning) {
                    Intent intent = new Intent(MainActivity.this, ShimejiService.class);
                    intent.setAction(ShimejiService.ACTION_CLEAR_EXTRAS);
                    startService(intent);
                    Toast.makeText(MainActivity.this, "Extras limpiados", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(MainActivity.this, "No hay Shimejis activos", Toast.LENGTH_SHORT).show();
                }
            }
        });

        btnSettingsStop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopShimeji();
            }
        });

        setupColorPaletteListeners();
        setupAiEngineListeners();
        setupCommandSlotsListeners();
        setupJarvisAgentListeners();
    }

    private void setupAiEngineListeners() {
        if (rgAiMode != null) {
            rgAiMode.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
                @Override
                public void onCheckedChanged(RadioGroup group, int checkedId) {
                    if (checkedId == R.id.rb_ai_gemini) {
                        if (layoutGeminiConfig != null) layoutGeminiConfig.setVisibility(View.VISIBLE);
                        if (layoutCloudConfig != null) layoutCloudConfig.setVisibility(View.GONE);
                        if (tvAiStatus != null) tvAiStatus.setText("Modo: Google Gemini API (Cloud).");
                    } else if (checkedId == R.id.rb_ai_cloud) {
                        if (layoutGeminiConfig != null) layoutGeminiConfig.setVisibility(View.GONE);
                        if (layoutCloudConfig != null) layoutCloudConfig.setVisibility(View.VISIBLE);
                        if (tvAiStatus != null) tvAiStatus.setText("Modo: Custom Cloud / Ollama / OpenAI REST API.");
                    } else {
                        if (layoutGeminiConfig != null) layoutGeminiConfig.setVisibility(View.GONE);
                        if (layoutCloudConfig != null) layoutCloudConfig.setVisibility(View.GONE);
                        if (tvAiStatus != null) tvAiStatus.setText("Modo: Local Offline activo (respuestas instantaneas).");
                    }
                }
            });
        }

        if (btnSaveAi != null) {
            btnSaveAi.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    String mode = "local";
                    if (rbAiGemini != null && rbAiGemini.isChecked()) mode = "gemini";
                    else if (rbAiCloud != null && rbAiCloud.isChecked()) mode = "cloud";

                    String gemKey = etGeminiKey != null ? etGeminiKey.getText().toString().trim() : "";
                    String gemModel = etGeminiModel != null ? etGeminiModel.getText().toString().trim() : "gemini-2.5-flash";
                    String clEndpoint = etCloudEndpoint != null ? etCloudEndpoint.getText().toString().trim() : "";
                    String clModel = etCloudModel != null ? etCloudModel.getText().toString().trim() : "llama3";
                    String clKey = etCloudKey != null ? etCloudKey.getText().toString().trim() : "";

                    prefs.edit()
                        .putString(KEY_AI_MODE, mode)
                        .putString(KEY_GEMINI_KEY, gemKey)
                        .putString(KEY_GEMINI_MODEL, gemModel)
                        .putString(KEY_CLOUD_ENDPOINT, clEndpoint)
                        .putString(KEY_CLOUD_MODEL, clModel)
                        .putString(KEY_CLOUD_KEY, clKey)
                        .apply();

                    Toast.makeText(MainActivity.this, "Configuracion de IA guardada en la app", Toast.LENGTH_SHORT).show();
                }
            });
        }

        if (btnTestAi != null) {
            btnTestAi.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    String mode = "local";
                    if (rbAiGemini != null && rbAiGemini.isChecked()) mode = "gemini";
                    else if (rbAiCloud != null && rbAiCloud.isChecked()) mode = "cloud";

                    String gemKey = etGeminiKey != null ? etGeminiKey.getText().toString().trim() : "";
                    String gemModel = etGeminiModel != null ? etGeminiModel.getText().toString().trim() : "gemini-2.5-flash";
                    String clEndpoint = etCloudEndpoint != null ? etCloudEndpoint.getText().toString().trim() : "";
                    String clKey = etCloudKey != null ? etCloudKey.getText().toString().trim() : "";

                    Toast.makeText(MainActivity.this, "Probando conexion con IA...", Toast.LENGTH_SHORT).show();
                    AiEngineHelper.testConnection(MainActivity.this, mode, mode.equals("gemini") ? gemKey : clKey, gemModel, clEndpoint, new AiEngineHelper.AiCallback() {
                        @Override
                        public void onSuccess(final String reply) {
                            Toast.makeText(MainActivity.this, "[IA Exito]: " + reply, Toast.LENGTH_LONG).show();
                        }

                        @Override
                        public void onError(final String errorMsg) {
                            Toast.makeText(MainActivity.this, "[IA Error]: " + errorMsg, Toast.LENGTH_LONG).show();
                        }
                    });
                }
            });
        }

        if (sbAiMaxTokens != null && tvAiMaxTokensVal != null) {
            int curTokens = prefs.getInt("ai_max_tokens", 4096);
            sbAiMaxTokens.setProgress(curTokens);
            tvAiMaxTokensVal.setText(String.valueOf(curTokens));
            sbAiMaxTokens.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                @Override
                public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                    int val = Math.max(256, progress);
                    tvAiMaxTokensVal.setText(String.valueOf(val));
                    prefs.edit().putInt("ai_max_tokens", val).apply();
                }
                @Override public void onStartTrackingTouch(SeekBar seekBar) {}
                @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            });
        }
    }

    private void setupCommandSlotsListeners() {
        if (btnAddCommandSlot != null) {
            btnAddCommandSlot.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showAddSlotDialog();
                }
            });
        }
    }

    public void refreshCommandSlotsUI() {
        if (layoutSlotsContainer == null) return;
        layoutSlotsContainer.removeAllViews();

        List<String> slots = CommandSlotHelper.getSlots(this);
        if (badgeSlotsCount != null) {
            badgeSlotsCount.setText(slots.size() + " ranuras");
        }

        if (slots.isEmpty()) {
            if (tvEmptySlots != null) {
                tvEmptySlots.setVisibility(View.VISIBLE);
                layoutSlotsContainer.addView(tvEmptySlots);
            }
            return;
        }

        if (tvEmptySlots != null) {
            tvEmptySlots.setVisibility(View.GONE);
        }

        for (int i = 0; i < slots.size(); i++) {
            final String slot = slots.get(i);
            final int slotIndex = i;

            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);
            row.setGravity(Gravity.CENTER_VERTICAL);
            row.setBackgroundResource(R.drawable.chip_action_bg);
            row.setPadding(dpToPx(12), dpToPx(8), dpToPx(12), dpToPx(8));
            LinearLayout.LayoutParams rowParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            rowParams.bottomMargin = dpToPx(6);
            row.setLayoutParams(rowParams);

            // Badge tipo
            TextView badge = new TextView(this);
            badge.setBackgroundResource(R.drawable.chip_tag_bg);
            badge.setTextColor(Color.parseColor("#B89FFF"));
            badge.setTextSize(10);
            badge.setTypeface(null, android.graphics.Typeface.BOLD);
            badge.setPadding(dpToPx(6), dpToPx(2), dpToPx(6), dpToPx(2));

            String badgeText = "X";
            if (slot.startsWith("abrirapp-")) badgeText = "APP";
            else if (slot.startsWith("ejecutarcomando-")) badgeText = "CMD";
            else if (slot.startsWith("decir-")) badgeText = "VOZ";
            else if (slot.startsWith("buscar-")) badgeText = "WEB";
            else if (slot.startsWith("accion-")) badgeText = "ACT";
            else if (slot.startsWith("crearcarpeta-")) badgeText = "DIR";
            badge.setText(badgeText);
            row.addView(badge);

            // Slot name
            TextView tvName = new TextView(this);
            LinearLayout.LayoutParams nameParams = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
            nameParams.leftMargin = dpToPx(8);
            tvName.setLayoutParams(nameParams);
            tvName.setText(slot);
            tvName.setTextColor(Color.parseColor("#F3F0FA"));
            tvName.setTextSize(12);
            row.addView(tvName);

            // Boton Probar
            TextView btnRun = new TextView(this);
            btnRun.setText("Ejecutar");
            btnRun.setTextColor(Color.parseColor("#86EFAC"));
            btnRun.setTextSize(11);
            btnRun.setPadding(dpToPx(6), dpToPx(4), dpToPx(6), dpToPx(4));
            btnRun.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    CommandSlotHelper.matchAndExecute(MainActivity.this, slot, new CommandSlotHelper.ExecutionCallback() {
                        @Override
                        public void onExecuted(boolean success, String reply) {
                            Toast.makeText(MainActivity.this, reply, Toast.LENGTH_SHORT).show();
                        }
                    });
                }
            });
            row.addView(btnRun);

            // Boton Eliminar
            TextView btnDelete = new TextView(this);
            btnDelete.setText("✕");
            btnDelete.setTextColor(Color.parseColor("#FCA5A5"));
            btnDelete.setTextSize(14);
            btnDelete.setPadding(dpToPx(8), dpToPx(4), dpToPx(4), dpToPx(4));
            btnDelete.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    CommandSlotHelper.removeSlot(MainActivity.this, slotIndex);
                    refreshCommandSlotsUI();
                    Toast.makeText(MainActivity.this, "Ranura eliminada", Toast.LENGTH_SHORT).show();
                }
            });
            row.addView(btnDelete);

            layoutSlotsContainer.addView(row);
        }
    }

    private void showAddSlotDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.parseColor("#181428"));
        root.setPadding(dpToPx(16), dpToPx(16), dpToPx(16), dpToPx(16));

        TextView tvTitle = new TextView(this);
        tvTitle.setText("Agregar Ranura Prefabicada");
        tvTitle.setTextColor(Color.parseColor("#F3F0FA"));
        tvTitle.setTextSize(16);
        tvTitle.setTypeface(null, android.graphics.Typeface.BOLD);
        tvTitle.setPadding(0, 0, 0, dpToPx(6));
        root.addView(tvTitle);

        TextView tvSubtitle = new TextView(this);
        tvSubtitle.setText("Elige una plantilla y completa unicamente el valor de [X]:");
        tvSubtitle.setTextColor(Color.parseColor("#A69DB8"));
        tvSubtitle.setTextSize(11);
        tvSubtitle.setPadding(0, 0, 0, dpToPx(12));
        root.addView(tvSubtitle);

        final String[] templates = {
            "abrirapp",
            "ejecutarcomando",
            "decir",
            "buscar",
            "accion",
            "crearcarpeta"
        };
        final String[] templateLabels = {
            "abrirapp-[X]  (Abrir aplicacion)",
            "ejecutarcomando-[X]  (Termux / Shell)",
            "decir-[X]  (Hacer hablar al Shimeji)",
            "buscar-[X]  (YouTube / Web)",
            "accion-[X]  (guitarra, caja, bailar)",
            "crearcarpeta-[X]  (Crear en Documents)"
        };

        final android.widget.Spinner spTemplate = new android.widget.Spinner(this);
        android.widget.ArrayAdapter<String> adapter = new android.widget.ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, templateLabels) {
            @Override
            public View getView(int position, View convertView, ViewGroup parent) {
                View v = super.getView(position, convertView, parent);
                if (v instanceof TextView) {
                    ((TextView) v).setTextColor(Color.parseColor("#E8DEFF"));
                    ((TextView) v).setTextSize(12);
                }
                return v;
            }
            @Override
            public View getDropDownView(int position, View convertView, ViewGroup parent) {
                View v = super.getDropDownView(position, convertView, parent);
                v.setBackgroundColor(Color.parseColor("#221C34"));
                if (v instanceof TextView) {
                    ((TextView) v).setTextColor(Color.parseColor("#F3F0FA"));
                    ((TextView) v).setTextSize(12);
                }
                return v;
            }
        };
        spTemplate.setAdapter(adapter);
        spTemplate.setBackgroundResource(R.drawable.edittext_bg);
        spTemplate.setPadding(dpToPx(10), dpToPx(8), dpToPx(10), dpToPx(8));
        LinearLayout.LayoutParams spParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(42));
        spParams.bottomMargin = dpToPx(12);
        spTemplate.setLayoutParams(spParams);
        root.addView(spTemplate);

        TextView tvLabelX = new TextView(this);
        tvLabelX.setText("Valor de [X]:");
        tvLabelX.setTextColor(Color.parseColor("#F3F0FA"));
        tvLabelX.setTextSize(12);
        tvLabelX.setPadding(0, 0, 0, dpToPx(4));
        root.addView(tvLabelX);

        final EditText etParamX = new EditText(this);
        etParamX.setHint("ej: tiktok, spotify, ls, hola...");
        etParamX.setHintTextColor(Color.parseColor("#5E5470"));
        etParamX.setTextColor(Color.parseColor("#F3F0FA"));
        etParamX.setTextSize(12);
        etParamX.setBackgroundResource(R.drawable.edittext_bg);
        etParamX.setPadding(dpToPx(12), dpToPx(8), dpToPx(12), dpToPx(8));
        LinearLayout.LayoutParams etParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(42));
        etParams.bottomMargin = dpToPx(10);
        etParamX.setLayoutParams(etParams);
        root.addView(etParamX);

        final TextView tvPreview = new TextView(this);
        tvPreview.setText("Comando: abrirapp-tiktok");
        tvPreview.setTextColor(Color.parseColor("#B89FFF"));
        tvPreview.setTextSize(12);
        tvPreview.setTypeface(null, android.graphics.Typeface.BOLD);
        tvPreview.setPadding(0, 0, 0, dpToPx(16));
        root.addView(tvPreview);

        android.text.TextWatcher watcher = new android.text.TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {}
            @Override
            public void afterTextChanged(android.text.Editable s) {
                int pos = spTemplate.getSelectedItemPosition();
                String tName = (pos >= 0 && pos < templates.length) ? templates[pos] : "abrirapp";
                String val = s.toString().trim();
                tvPreview.setText("Comando: " + tName + "-" + (val.isEmpty() ? "[X]" : val));
            }
        };
        etParamX.addTextChangedListener(watcher);
        spTemplate.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(android.widget.AdapterView<?> parent, View view, int position, long id) {
                String tName = (position >= 0 && position < templates.length) ? templates[position] : "abrirapp";
                String val = etParamX.getText().toString().trim();
                tvPreview.setText("Comando: " + tName + "-" + (val.isEmpty() ? "[X]" : val));
            }
            @Override public void onNothingSelected(android.widget.AdapterView<?> parent) {}
        });

        builder.setView(root);
        builder.setPositiveButton("Guardar Ranura", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                int pos = spTemplate.getSelectedItemPosition();
                String tName = (pos >= 0 && pos < templates.length) ? templates[pos] : "abrirapp";
                String val = etParamX.getText().toString().trim();
                if (val.isEmpty()) {
                    Toast.makeText(MainActivity.this, "Debes ingresar el valor de X", Toast.LENGTH_SHORT).show();
                    return;
                }
                String slot = tName + "-" + val;
                boolean added = CommandSlotHelper.addSlot(MainActivity.this, slot);
                refreshCommandSlotsUI();
                if (added) {
                    Toast.makeText(MainActivity.this, "Ranura '" + slot + "' guardada", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(MainActivity.this, "La ranura ya existe", Toast.LENGTH_SHORT).show();
                }
            }
        });
        builder.setNegativeButton("Cancelar", null);
        AlertDialog dialog = builder.create();
        dialog.show();
    }

    private void setupJarvisAgentListeners() {
        if (etJarvisName != null) {
            etJarvisName.setText(prefs.getString("assistant_name", "Jarvis"));
        }
        if (etJarvisPrompt != null) {
            etJarvisPrompt.setText(prefs.getString("agent_extra_prompt", ""));
        }
        if (cbJarvisUseSkin != null) {
            cbJarvisUseSkin.setChecked(prefs.getBoolean("agent_use_skin_persona", true));
        }

        // Steps
        if (sbJarvisSteps != null) {
            int steps = prefs.getInt("agent_max_steps", 6);
            sbJarvisSteps.setProgress(Math.max(1, Math.min(10, steps)));
            if (badgeJarvisSteps != null) badgeJarvisSteps.setText(sbJarvisSteps.getProgress() + " pasos");
            sbJarvisSteps.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                    if (progress < 1) progress = 1;
                    if (badgeJarvisSteps != null) badgeJarvisSteps.setText(progress + " pasos");
                }
                @Override public void onStartTrackingTouch(SeekBar seekBar) {}
                @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            });
        }

        // Permisos
        if (cbPermApps != null) cbPermApps.setChecked(prefs.getBoolean("perm_apps", true));
        if (cbPermSystem != null) cbPermSystem.setChecked(prefs.getBoolean("perm_system", true));
        if (cbPermReminders != null) cbPermReminders.setChecked(prefs.getBoolean("perm_reminders", true));
        if (cbPermFilesWrite != null) cbPermFilesWrite.setChecked(prefs.getBoolean("perm_files_write", true));
        if (cbPermFilesDelete != null) cbPermFilesDelete.setChecked(prefs.getBoolean("perm_files_delete", false));
        if (cbPermShell != null) cbPermShell.setChecked(prefs.getBoolean("perm_shell", false));

        // Accesibilidad
        if (btnJarvisAccessibility != null) {
            btnJarvisAccessibility.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    try {
                        Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
                        startActivity(intent);
                        Toast.makeText(MainActivity.this, "Busca 'PinkChan Shimeji JARVIS' y activalo", Toast.LENGTH_LONG).show();
                    } catch (Exception e) {
                        Toast.makeText(MainActivity.this, "No se pudo abrir ajustes de accesibilidad", Toast.LENGTH_SHORT).show();
                    }
                }
            });
        }

        // TTS
        if (cbJarvisTts != null) cbJarvisTts.setChecked(prefs.getBoolean("tts_enabled", false));
        if (sbTtsRate != null) {
            int rateVal = (int) (prefs.getFloat("tts_rate", 1.0f) * 10);
            sbTtsRate.setProgress(Math.max(5, Math.min(20, rateVal)));
            if (tvTtsRateVal != null) tvTtsRateVal.setText(String.format(Locale.US, "%.1fx", sbTtsRate.getProgress() / 10.0f));
            sbTtsRate.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                    if (progress < 5) progress = 5;
                    if (tvTtsRateVal != null) tvTtsRateVal.setText(String.format(Locale.US, "%.1fx", progress / 10.0f));
                }
                @Override public void onStartTrackingTouch(SeekBar seekBar) {}
                @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            });
        }
        if (sbTtsPitch != null) {
            int pitchVal = (int) (prefs.getFloat("tts_pitch", 1.0f) * 10);
            sbTtsPitch.setProgress(Math.max(5, Math.min(20, pitchVal)));
            if (tvTtsPitchVal != null) tvTtsPitchVal.setText(String.format(Locale.US, "%.1fx", sbTtsPitch.getProgress() / 10.0f));
            sbTtsPitch.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                    if (progress < 5) progress = 5;
                    if (tvTtsPitchVal != null) tvTtsPitchVal.setText(String.format(Locale.US, "%.1fx", progress / 10.0f));
                }
                @Override public void onStartTrackingTouch(SeekBar seekBar) {}
                @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            });
        }

        if (btnJarvisTestTts != null) {
            btnJarvisTestTts.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    String name = etJarvisName != null ? etJarvisName.getText().toString().trim() : "Jarvis";
                    if (name.isEmpty()) name = "Jarvis";
                    String testPhrase = "Hola, soy " + name + ", tu asistente inteligente.";
                    ShimejiService s = ShimejiService.getInstance();
                    if (s != null) {
                        float r = sbTtsRate != null ? (sbTtsRate.getProgress() / 10.0f) : 1.0f;
                        float p = sbTtsPitch != null ? (sbTtsPitch.getProgress() / 10.0f) : 1.0f;
                        prefs.edit().putFloat("tts_rate", r).putFloat("tts_pitch", p).putBoolean("tts_enabled", true).apply();
                        s.syncTtsSettings();
                        s.speakTts(testPhrase);
                    } else {
                        Toast.makeText(MainActivity.this, "[TTS]: " + testPhrase, Toast.LENGTH_SHORT).show();
                    }
                }
            });
        }

        // Wake Word
        if (cbJarvisWakeWord != null) cbJarvisWakeWord.setChecked(prefs.getBoolean("wake_word_enabled", false));
        if (etJarvisWakePhrase != null) etJarvisWakePhrase.setText(prefs.getString("wake_word_phrase", "oye jarvis"));

        if (btnJarvisPushToTalk != null) {
            btnJarvisPushToTalk.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    ShimejiService s = ShimejiService.getInstance();
                    if (s != null) {
                        s.startVoiceAssistant();
                        Toast.makeText(MainActivity.this, "Escuchando... Di tu comando", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(MainActivity.this, "Inicia los Shimejis primero para usar el asistente de voz", Toast.LENGTH_LONG).show();
                    }
                }
            });
        }

        // Shimeji Behavior
        if (sbShimejiSpeed != null) {
            int spdVal = (int) (prefs.getFloat("shimeji_walk_speed_mult", 1.0f) * 10);
            sbShimejiSpeed.setProgress(Math.max(5, Math.min(30, spdVal)));
            if (tvShimejiSpeedVal != null) tvShimejiSpeedVal.setText(String.format(Locale.US, "%.1fx", sbShimejiSpeed.getProgress() / 10.0f));
            sbShimejiSpeed.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                    if (progress < 5) progress = 5;
                    if (tvShimejiSpeedVal != null) tvShimejiSpeedVal.setText(String.format(Locale.US, "%.1fx", progress / 10.0f));
                }
                @Override public void onStartTrackingTouch(SeekBar seekBar) {}
                @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            });
        }
        if (sbShimejiGravity != null) {
            int grvVal = (int) (prefs.getFloat("shimeji_gravity_mult", 1.0f) * 10);
            sbShimejiGravity.setProgress(Math.max(2, Math.min(30, grvVal)));
            if (tvShimejiGravityVal != null) tvShimejiGravityVal.setText(String.format(Locale.US, "%.1fx", sbShimejiGravity.getProgress() / 10.0f));
            sbShimejiGravity.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                    if (progress < 2) progress = 2;
                    if (tvShimejiGravityVal != null) tvShimejiGravityVal.setText(String.format(Locale.US, "%.1fx", progress / 10.0f));
                }
                @Override public void onStartTrackingTouch(SeekBar seekBar) {}
                @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            });
        }
        if (sbShimejiTalk != null) {
            int talkVal = prefs.getInt("shimeji_talk_interval_sec", 45);
            sbShimejiTalk.setProgress(Math.max(10, Math.min(180, talkVal)));
            if (tvShimejiTalkVal != null) tvShimejiTalkVal.setText(sbShimejiTalk.getProgress() + "s");
            sbShimejiTalk.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                    if (progress < 10) progress = 10;
                    if (tvShimejiTalkVal != null) tvShimejiTalkVal.setText(progress + "s");
                }
                @Override public void onStartTrackingTouch(SeekBar seekBar) {}
                @Override public void onStopTrackingTouch(SeekBar seekBar) {}
            });
        }

        if (cbAllowWallClimb != null) cbAllowWallClimb.setChecked(prefs.getBoolean("allow_wall_climb", true));
        if (cbAllowCeiling != null) cbAllowCeiling.setChecked(prefs.getBoolean("allow_ceiling", true));
        if (cbAllowSitting != null) cbAllowSitting.setChecked(prefs.getBoolean("allow_sitting", true));
        if (cbAllowCustomActions != null) cbAllowCustomActions.setChecked(prefs.getBoolean("allow_custom_actions", true));

        // Chat
        if (cbChatPosLocked != null) cbChatPosLocked.setChecked(prefs.getBoolean("chat_pos_locked", false));

        // Macros
        refreshMacrosUI();
        if (btnLoadPrebuiltMacros != null) {
            btnLoadPrebuiltMacros.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    loadPrebuiltMacros();
                }
            });
        }
        if (btnAddJarvisMacro != null) {
            btnAddJarvisMacro.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    showAddMacroDialog();
                }
            });
        }

        // Save All Button
        if (btnSaveJarvisAll != null) {
            btnSaveJarvisAll.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    saveAllJarvisSettings();
                }
            });
        }
    }

    private void saveAllJarvisSettings() {
        String name = etJarvisName != null ? etJarvisName.getText().toString().trim() : "Jarvis";
        if (name.isEmpty()) name = "Jarvis";
        String prompt = etJarvisPrompt != null ? etJarvisPrompt.getText().toString().trim() : "";
        boolean useSkin = cbJarvisUseSkin == null || cbJarvisUseSkin.isChecked();
        int steps = sbJarvisSteps != null ? Math.max(1, sbJarvisSteps.getProgress()) : 6;

        boolean pApps = cbPermApps == null || cbPermApps.isChecked();
        boolean pSys = cbPermSystem == null || cbPermSystem.isChecked();
        boolean pRem = cbPermReminders == null || cbPermReminders.isChecked();
        boolean pWrite = cbPermFilesWrite == null || cbPermFilesWrite.isChecked();
        boolean pDel = cbPermFilesDelete != null && cbPermFilesDelete.isChecked();
        boolean pShell = cbPermShell != null && cbPermShell.isChecked();

        boolean ttsOn = cbJarvisTts != null && cbJarvisTts.isChecked();
        float ttsRate = sbTtsRate != null ? (sbTtsRate.getProgress() / 10.0f) : 1.0f;
        float ttsPitch = sbTtsPitch != null ? (sbTtsPitch.getProgress() / 10.0f) : 1.0f;

        boolean wakeOn = cbJarvisWakeWord != null && cbJarvisWakeWord.isChecked();
        String wakePhrase = etJarvisWakePhrase != null ? etJarvisWakePhrase.getText().toString().trim() : "oye jarvis";
        if (wakePhrase.isEmpty()) wakePhrase = "oye jarvis";

        float spdMult = sbShimejiSpeed != null ? (sbShimejiSpeed.getProgress() / 10.0f) : 1.0f;
        float grvMult = sbShimejiGravity != null ? (sbShimejiGravity.getProgress() / 10.0f) : 1.0f;
        int talkSec = sbShimejiTalk != null ? sbShimejiTalk.getProgress() : 45;

        boolean allowClimb = cbAllowWallClimb == null || cbAllowWallClimb.isChecked();
        boolean allowCeil = cbAllowCeiling == null || cbAllowCeiling.isChecked();
        boolean allowSit = cbAllowSitting == null || cbAllowSitting.isChecked();
        boolean allowCustom = cbAllowCustomActions == null || cbAllowCustomActions.isChecked();

        boolean chatLocked = cbChatPosLocked != null && cbChatPosLocked.isChecked();

        prefs.edit()
            .putString("assistant_name", name)
            .putString("agent_extra_prompt", prompt)
            .putBoolean("agent_use_skin_persona", useSkin)
            .putInt("agent_max_steps", steps)
            .putBoolean("perm_apps", pApps)
            .putBoolean("perm_system", pSys)
            .putBoolean("perm_reminders", pRem)
            .putBoolean("perm_files_write", pWrite)
            .putBoolean("perm_files_delete", pDel)
            .putBoolean("perm_shell", pShell)
            .putBoolean("tts_enabled", ttsOn)
            .putFloat("tts_rate", ttsRate)
            .putFloat("tts_pitch", ttsPitch)
            .putBoolean("wake_word_enabled", wakeOn)
            .putString("wake_word_phrase", wakePhrase)
            .putFloat("shimeji_walk_speed_mult", spdMult)
            .putFloat("shimeji_gravity_mult", grvMult)
            .putInt("shimeji_talk_interval_sec", talkSec)
            .putBoolean("allow_wall_climb", allowClimb)
            .putBoolean("allow_ceiling", allowCeil)
            .putBoolean("allow_sitting", allowSit)
            .putBoolean("allow_custom_actions", allowCustom)
            .putBoolean("chat_pos_locked", chatLocked)
            .apply();

        ShimejiService s = ShimejiService.getInstance();
        if (s != null) {
            s.syncTtsSettings();
            s.syncWakeWordState();
        }

        Toast.makeText(this, "Ajustes de JARVIS y personalizacion guardados", Toast.LENGTH_SHORT).show();
    }

    public void refreshMacrosUI() {
        if (layoutMacrosContainer == null) return;
        layoutMacrosContainer.removeAllViews();

        String raw = prefs.getString(AgentToolExecutor.PREF_MACROS, "{}");
        try {
            JSONObject obj = new JSONObject(raw);
            if (obj.length() == 0) {
                JSONArray sample = new JSONArray();
                sample.put("[JARVIS: VOLUME 80]");
                sample.put("[JARVIS: SEARCH_YT \"chill beats\"]");
                obj.put("Modo Relax", sample);
                prefs.edit().putString(AgentToolExecutor.PREF_MACROS, obj.toString()).apply();
            }

            java.util.Iterator<String> keys = obj.keys();
            while (keys.hasNext()) {
                final String macroName = keys.next();
                final JSONArray steps = obj.getJSONArray(macroName);

                LinearLayout row = new LinearLayout(this);
                row.setOrientation(LinearLayout.HORIZONTAL);
                row.setGravity(Gravity.CENTER_VERTICAL);
                row.setBackgroundResource(R.drawable.chip_tag_bg);
                row.setPadding(dpToPx(12), dpToPx(8), dpToPx(8), dpToPx(8));
                LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
                lp.bottomMargin = dpToPx(6);
                row.setLayoutParams(lp);

                TextView tvName = new TextView(this);
                tvName.setText(macroName + " (" + steps.length() + " pasos)");
                tvName.setTextColor(Color.parseColor("#EDE9FE"));
                tvName.setTextSize(12);
                tvName.setTypeface(null, android.graphics.Typeface.BOLD);
                LinearLayout.LayoutParams nameLp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
                tvName.setLayoutParams(nameLp);
                row.addView(tvName);

                // Boton Ejecutar
                TextView btnRun = new TextView(this);
                btnRun.setText("Ejecutar");
                btnRun.setTextColor(Color.parseColor("#A78BFA"));
                btnRun.setTextSize(11);
                btnRun.setPadding(dpToPx(8), dpToPx(4), dpToPx(8), dpToPx(4));
                btnRun.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        new Thread(new Runnable() {
                            @Override
                            public void run() {
                                final String res = AgentToolExecutor.runMacro(MainActivity.this, macroName);
                                runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        Toast.makeText(MainActivity.this, res, Toast.LENGTH_LONG).show();
                                    }
                                });
                            }
                        }).start();
                    }
                });
                row.addView(btnRun);

                // Boton Eliminar
                TextView btnDel = new TextView(this);
                btnDel.setText("✕");
                btnDel.setTextColor(Color.parseColor("#FCA5A5"));
                btnDel.setTextSize(13);
                btnDel.setPadding(dpToPx(8), dpToPx(4), dpToPx(4), dpToPx(4));
                btnDel.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        try {
                            String cur = prefs.getString(AgentToolExecutor.PREF_MACROS, "{}");
                            JSONObject o = new JSONObject(cur);
                            o.remove(macroName);
                            prefs.edit().putString(AgentToolExecutor.PREF_MACROS, o.toString()).apply();
                            refreshMacrosUI();
                            Toast.makeText(MainActivity.this, "Macro eliminada", Toast.LENGTH_SHORT).show();
                        } catch (Exception ignored) {}
                    }
                });
                row.addView(btnDel);

                layoutMacrosContainer.addView(row);
            }
        } catch (Exception e) {
            TextView err = new TextView(this);
            err.setText("Sin macros configuradas");
            err.setTextColor(Color.parseColor("#9CA3AF"));
            err.setTextSize(11);
            layoutMacrosContainer.addView(err);
        }
    }

    private void showAddMacroDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.parseColor("#181428"));
        root.setPadding(dpToPx(16), dpToPx(16), dpToPx(16), dpToPx(16));

        TextView tvTitle = new TextView(this);
        tvTitle.setText("Nueva Macro Multitarea");
        tvTitle.setTextColor(Color.parseColor("#F3F0FA"));
        tvTitle.setTextSize(16);
        tvTitle.setTypeface(null, android.graphics.Typeface.BOLD);
        tvTitle.setPadding(0, 0, 0, dpToPx(6));
        root.addView(tvTitle);

        TextView tvDesc = new TextView(this);
        tvDesc.setText("Escribe los pasos separados por linea (ej: [JARVIS: VOLUME 50], [JARVIS: OPEN \"tiktok\"] o WAIT 2):");
        tvDesc.setTextColor(Color.parseColor("#A69DB8"));
        tvDesc.setTextSize(11);
        tvDesc.setPadding(0, 0, 0, dpToPx(8));
        root.addView(tvDesc);

        final EditText etName = new EditText(this);
        etName.setHint("Nombre de la macro (ej: Mi Rutina)");
        etName.setTextColor(Color.WHITE);
        etName.setHintTextColor(Color.parseColor("#6B7280"));
        etName.setTextSize(12);
        etName.setBackgroundResource(R.drawable.edittext_bg);
        etName.setPadding(dpToPx(10), dpToPx(8), dpToPx(10), dpToPx(8));
        LinearLayout.LayoutParams nLp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(40));
        nLp.bottomMargin = dpToPx(8);
        etName.setLayoutParams(nLp);
        root.addView(etName);

        final EditText etSteps = new EditText(this);
        etSteps.setHint("[JARVIS: VOLUME 70]\nWAIT 1\n[JARVIS: SEARCH_YT \"bocchi\"]");
        etSteps.setTextColor(Color.WHITE);
        etSteps.setHintTextColor(Color.parseColor("#6B7280"));
        etSteps.setTextSize(11);
        etSteps.setGravity(Gravity.TOP | Gravity.START);
        etSteps.setBackgroundResource(R.drawable.edittext_bg);
        etSteps.setPadding(dpToPx(10), dpToPx(8), dpToPx(10), dpToPx(8));
        LinearLayout.LayoutParams sLp = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(90));
        etSteps.setLayoutParams(sLp);
        root.addView(etSteps);

        builder.setView(root);
        builder.setPositiveButton("Guardar Macro", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                String name = etName.getText().toString().trim();
                String stepsText = etSteps.getText().toString().trim();
                if (name.isEmpty() || stepsText.isEmpty()) {
                    Toast.makeText(MainActivity.this, "Nombre y pasos requeridos", Toast.LENGTH_SHORT).show();
                    return;
                }
                try {
                    String cur = prefs.getString(AgentToolExecutor.PREF_MACROS, "{}");
                    JSONObject o = new JSONObject(cur);
                    JSONArray arr = new JSONArray();
                    String[] lines = stepsText.split("\n");
                    for (String line : lines) {
                        String l = line.trim();
                        if (!l.isEmpty()) arr.put(l);
                    }
                    o.put(name, arr);
                    prefs.edit().putString(AgentToolExecutor.PREF_MACROS, o.toString()).apply();
                    refreshMacrosUI();
                    Toast.makeText(MainActivity.this, "Macro '" + name + "' guardada", Toast.LENGTH_SHORT).show();
                } catch (Exception e) {
                    Toast.makeText(MainActivity.this, "Error guardando macro: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });
        builder.setNegativeButton("Cancelar", null);
        builder.show();
    }

    private void updateInspectorMascot(String skinId) {
        if (ivInspectorMascot == null) return;
        int resId = R.drawable.ic_konata;
        if ("Bocchi".equalsIgnoreCase(skinId)) resId = R.drawable.ic_bocchi;
        else if ("Monika".equalsIgnoreCase(skinId)) resId = R.drawable.ic_monika;
        else if ("Natsuki".equalsIgnoreCase(skinId)) resId = R.drawable.ic_natsuki;
        else if ("Sayori".equalsIgnoreCase(skinId)) resId = R.drawable.ic_sayori;
        else if ("Yuri".equalsIgnoreCase(skinId)) resId = R.drawable.ic_yuri;
        else if ("Hachi".equalsIgnoreCase(skinId)) resId = R.drawable.ic_hachi;
        else if ("Usagi".equalsIgnoreCase(skinId)) resId = R.drawable.ic_usagi;
        else if ("Pusheen".equalsIgnoreCase(skinId)) resId = R.drawable.ic_pusheen;
        ivInspectorMascot.setImageResource(resId);
    }

    private void spawnOrSelectSkin(String skinId) {
        if (!checkOverlayPermission()) {
            Toast.makeText(this, "Concede el permiso de superposicion primero", Toast.LENGTH_LONG).show();
            requestOverlayPermission();
            return;
        }

        prefs.edit().putString(KEY_SKIN, skinId).apply();
        updateInspectorMascot(skinId);

        if (ShimejiService.isRunning) {
            Intent intent = new Intent(this, ShimejiService.class);
            intent.setAction(ShimejiService.ACTION_SET_SKIN);
            intent.putExtra(ShimejiService.EXTRA_SKIN, skinId);
            startService(intent);
            Toast.makeText(this, skinId + " activo en pantalla", Toast.LENGTH_SHORT).show();
        } else {
            startShimejiWithSkin(skinId);
        }
        updateStatus();
    }

    private void startShimejiWithSkin(String skinId) {
        if (!checkOverlayPermission()) {
            requestOverlayPermission();
            return;
        }

        Intent intent = new Intent(this, ShimejiService.class);
        intent.setAction(ShimejiService.ACTION_START);
        intent.putExtra(ShimejiService.EXTRA_SKIN, skinId);
        intent.putExtra(ShimejiService.EXTRA_SIZE_DP, getSelectedSizeDp());
        intent.putExtra(ShimejiService.EXTRA_ZERO_GRAVITY, cbSettingsZeroG.isChecked());

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent);
        } else {
            startService(intent);
        }

        Toast.makeText(this, "Shimeji (" + skinId + ") activado", Toast.LENGTH_SHORT).show();
        updateStatus();
    }

    private void stopShimeji() {
        Intent intent = new Intent(this, ShimejiService.class);
        stopService(intent);
        Toast.makeText(this, "Todos los Shimejis han sido detenidos", Toast.LENGTH_SHORT).show();
        updateStatus();
    }

    private void triggerAction(String actionName) {
        if (ShimejiService.isRunning) {
            Intent intent = new Intent(this, ShimejiService.class);
            intent.setAction(ShimejiService.ACTION_TRIGGER);
            intent.putExtra(ShimejiService.EXTRA_TRIGGER_ACTION, actionName);
            startService(intent);
        } else {
            Toast.makeText(this, "Inicia el Shimeji primero", Toast.LENGTH_SHORT).show();
        }
    }

    private int getSelectedSizeDp() {
        int checkedId = rgSettingsSize.getCheckedRadioButtonId();
        if (checkedId == R.id.rb_size_96) return 96;
        if (checkedId == R.id.rb_size_160) return 160;
        return 128;
    }

    private void checkAndStartVoiceAssistant() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQUEST_RECORD_AUDIO_PERMISSION);
                return;
            }
        }
        triggerVoiceAssistantService();
    }

    private void triggerVoiceAssistantService() {
        Intent intent = new Intent(this, ShimejiService.class);
        intent.setAction(ShimejiService.ACTION_START_VOICE);
        startService(intent);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_RECORD_AUDIO_PERMISSION) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                triggerVoiceAssistantService();
            } else {
                Toast.makeText(this, "Permiso de microfono necesario para el asistente", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private boolean checkOverlayPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            return Settings.canDrawOverlays(this);
        }
        return true;
    }

    private void requestOverlayPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!Settings.canDrawOverlays(this)) {
                Intent intent = new Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:" + getPackageName())
                );
                startActivityForResult(intent, REQUEST_OVERLAY_PERMISSION);
            } else {
                Toast.makeText(this, "Permiso de superposicion ya concedido", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void updatePermissionUI() {
        boolean granted = checkOverlayPermission();
        if (granted) {
            btnSettingsPermission.setText("Permiso de Superposicion [OK]");
            btnSettingsPermission.setAlpha(0.7f);
        } else {
            btnSettingsPermission.setText("Conceder Permiso de Superposicion");
            btnSettingsPermission.setAlpha(1.0f);
        }
    }

    private void updateStatus() {
        boolean running = ShimejiService.isRunning;
        if (tvActiveOverlayCount != null) {
            tvActiveOverlayCount.setText(running ? "Activo en pantalla" : "Inactivo");
        }
        if (tvInspectorStatus != null) {
            tvInspectorStatus.setText(running
                ? "Shimeji activo y caminando en tu pantalla."
                : "Nothing to inspect. Try spawning some shimeji!");
        }
    }

    private void restoreSavedPreferences() {
        int savedSize = prefs.getInt(KEY_SIZE, 128);
        if (savedSize == 96) {
            rgSettingsSize.check(R.id.rb_size_96);
            badgeSizeNum.setText("96 dp");
        } else if (savedSize == 160) {
            rgSettingsSize.check(R.id.rb_size_160);
            badgeSizeNum.setText("160 dp");
        } else {
            rgSettingsSize.check(R.id.rb_size_128);
            badgeSizeNum.setText("128 dp");
        }

        cbSettingsZeroG.setChecked(prefs.getBoolean(KEY_ZERO_G, false));

        int savedAlpha = prefs.getInt(KEY_BUBBLE_ALPHA, 90);
        boolean savedBorder = prefs.getBoolean(KEY_BUBBLE_BORDER, true);
        if (sbBubbleAlpha != null) {
            sbBubbleAlpha.setProgress(savedAlpha);
        }
        if (badgeBubbleAlpha != null) {
            badgeBubbleAlpha.setText(savedAlpha + "% Opacidad");
        }
        if (cbBubbleBorder != null) {
            cbBubbleBorder.setChecked(savedBorder);
        }

        String savedSkin = prefs.getString(KEY_SKIN, "Konata");
        updateInspectorMascot(savedSkin);

        int savedAccent = prefs.getInt("selected_accent_index", 0);
        int[] colorResIds = {
            R.color.palette_color_1, R.color.palette_color_2, R.color.palette_color_3,
            R.color.palette_color_4, R.color.palette_color_5, R.color.palette_color_6
        };
        String[] colorNames = {
            "Violeta Real", "Lavanda Suave", "Rosa Pastel",
            "Ambar Calido", "Menta Fresca", "Cielo Pastel"
        };
        if (savedAccent >= 0 && savedAccent < colorResIds.length) {
            applyAccentColor(colorResIds[savedAccent], colorNames[savedAccent], savedAccent);
        }

        // Restaurar Motor de IA
        String savedAiMode = prefs.getString(KEY_AI_MODE, "local");
        if ("gemini".equalsIgnoreCase(savedAiMode)) {
            if (rbAiGemini != null) rbAiGemini.setChecked(true);
            if (layoutGeminiConfig != null) layoutGeminiConfig.setVisibility(View.VISIBLE);
            if (layoutCloudConfig != null) layoutCloudConfig.setVisibility(View.GONE);
            if (tvAiStatus != null) tvAiStatus.setText("Modo: Google Gemini API (Cloud).");
        } else if ("cloud".equalsIgnoreCase(savedAiMode)) {
            if (rbAiCloud != null) rbAiCloud.setChecked(true);
            if (layoutGeminiConfig != null) layoutGeminiConfig.setVisibility(View.GONE);
            if (layoutCloudConfig != null) layoutCloudConfig.setVisibility(View.VISIBLE);
            if (tvAiStatus != null) tvAiStatus.setText("Modo: Custom Cloud / Ollama / OpenAI REST API.");
        } else {
            if (rbAiLocal != null) rbAiLocal.setChecked(true);
            if (layoutGeminiConfig != null) layoutGeminiConfig.setVisibility(View.GONE);
            if (layoutCloudConfig != null) layoutCloudConfig.setVisibility(View.GONE);
            if (tvAiStatus != null) tvAiStatus.setText("Modo: Local Offline activo (respuestas instantaneas).");
        }

        if (etGeminiKey != null) etGeminiKey.setText(prefs.getString(KEY_GEMINI_KEY, ""));
        if (etGeminiModel != null) etGeminiModel.setText(prefs.getString(KEY_GEMINI_MODEL, "gemini-2.5-flash"));
        if (etCloudEndpoint != null) etCloudEndpoint.setText(prefs.getString(KEY_CLOUD_ENDPOINT, ""));
        if (etCloudModel != null) etCloudModel.setText(prefs.getString(KEY_CLOUD_MODEL, "llama3"));
        if (etCloudKey != null) etCloudKey.setText(prefs.getString(KEY_CLOUD_KEY, ""));

        // Restaurar Ranuras Prefabicadas
        refreshCommandSlotsUI();
    }

    private void setupColorPaletteListeners() {
        int[] colorCircleIds = {
            R.id.iv_color_1, R.id.iv_color_2, R.id.iv_color_3,
            R.id.iv_color_4, R.id.iv_color_5, R.id.iv_color_6
        };
        final int[] colorResIds = {
            R.color.palette_color_1, R.color.palette_color_2, R.color.palette_color_3,
            R.color.palette_color_4, R.color.palette_color_5, R.color.palette_color_6
        };
        final String[] colorNames = {
            "Violeta Real", "Lavanda Suave", "Rosa Pastel",
            "Ambar Calido", "Menta Fresca", "Cielo Pastel"
        };

        for (int i = 0; i < colorCircleIds.length; i++) {
            final int index = i;
            final View iv = findViewById(colorCircleIds[i]);
            if (iv != null) {
                iv.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        applyAccentColor(colorResIds[index], colorNames[index], index);
                    }
                });
            }
        }
    }

    private void applyAccentColor(int colorResId, String colorName, int index) {
        currentAccentColor = getResources().getColor(colorResId);
        prefs.edit().putInt("selected_accent_index", index).apply();

        ColorStateList tintList = ColorStateList.valueOf(currentAccentColor);

        int[] colorCircleIds = {
            R.id.iv_color_1, R.id.iv_color_2, R.id.iv_color_3,
            R.id.iv_color_4, R.id.iv_color_5, R.id.iv_color_6
        };
        for (int i = 0; i < colorCircleIds.length; i++) {
            View circle = findViewById(colorCircleIds[i]);
            if (circle != null) {
                circle.setScaleX(i == index ? 1.3f : 1.0f);
                circle.setScaleY(i == index ? 1.3f : 1.0f);
                circle.setAlpha(i == index ? 1.0f : 0.6f);
            }
        }

        // Tint all buttons across the application
        Button[] allButtons = {
            btnSpawnKonata, btnSpawnBocchi, btnSpawnMonika, btnSpawnNatsuki, btnSpawnSayori, btnSpawnYuri,
            btnSpawnHachi, btnSpawnUsagi, btnSpawnPusheen,
            btnListSpawnKonata, btnListSpawnBocchi, btnListSpawnMonika, btnListSpawnNatsuki, btnListSpawnSayori,
            btnListSpawnYuri, btnListSpawnHachi, btnListSpawnUsagi, btnListSpawnPusheen, btnAddCategories,
            btnSpawnCustom, btnInteractionButton, btnCustomizeViews, btnInspectorVoice, btnInspectorGuitar,
            btnInspectorBox, btnInspectorCenter, btnInspectorPlay, btnInspectorDance, btnInspectorTermux,
            btnInspectorFiles, btnSettingsPermission, btnSettingsAppFilter, btnSettingsClearExtras
        };
        for (Button b : allButtons) {
            if (b != null) {
                b.setBackgroundTintList(tintList);
            }
        }

        if (badgePremium != null) {
            badgePremium.setBackgroundTintList(tintList);
        }

        if (tvActiveOverlayCount != null) {
            tvActiveOverlayCount.setTextColor(currentAccentColor);
        }
        if (badgeSizeNum != null) {
            badgeSizeNum.setTextColor(currentAccentColor);
        }
        if (tvAppTitle != null) {
            tvAppTitle.setTextColor(currentAccentColor);
        }

        if (cbSettingsZeroG != null) {
            cbSettingsZeroG.setButtonTintList(tintList);
        }
        if (rgSettingsSize != null) {
            for (int i = 0; i < rgSettingsSize.getChildCount(); i++) {
                View child = rgSettingsSize.getChildAt(i);
                if (child instanceof RadioButton) {
                    ((RadioButton) child).setButtonTintList(tintList);
                }
            }
        }

        // Re-apply tab coloring with currentAccentColor
        selectTab(currentTabIndex);

        Toast.makeText(this, "Tema aplicado: " + colorName, Toast.LENGTH_SHORT).show();
    }

    private void launchTermux() {
        PackageManager pm = getPackageManager();
        Intent launch = pm.getLaunchIntentForPackage("com.termux");
        if (launch != null) {
            launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(launch);
            Toast.makeText(this, "Iniciando Termux...", Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(this, "Termux no esta instalado (com.termux). Puedes descargarlo desde F-Droid.", Toast.LENGTH_LONG).show();
            try {
                Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://f-droid.org/packages/com.termux/"));
                startActivity(browserIntent);
            } catch (Exception ignored) {}
        }
    }

    private void createDemoFilesAndFolders() {
        try {
            java.io.File dir = new java.io.File(android.os.Environment.getExternalStoragePublicDirectory(android.os.Environment.DIRECTORY_DOCUMENTS), "Shijima");
            if (!dir.exists()) {
                dir.mkdirs();
            }
            java.io.File file = new java.io.File(dir, "shijima_quick_notes.txt");
            java.io.FileWriter writer = new java.io.FileWriter(file, false);
            writer.write("# Shijima Desktop Companion - Comandos y Notas\n");
            writer.write("Fecha de creacion: " + new java.util.Date() + "\n\n");
            writer.write("Comandos utiles para Termux:\n");
            writer.write("1. pkg update && pkg upgrade\n");
            writer.write("2. pkg install python git curl neofetch\n");
            writer.write("3. termux-setup-storage\n");
            writer.write("4. ls -la ~/storage/shared/Documents/Shijima/\n");
            writer.close();

            java.io.File localDir = new java.io.File(getExternalFilesDir(null), "Shijima");
            if (!localDir.exists()) localDir.mkdirs();
            java.io.File localFile = new java.io.File(localDir, "shijima_quick_notes.txt");
            java.io.FileWriter localWriter = new java.io.FileWriter(localFile, false);
            localWriter.write("Notas creadas correctamente.\n");
            localWriter.close();

            Toast.makeText(this, "Carpeta y notas creadas en Documents/Shijima", Toast.LENGTH_LONG).show();
            if (ShimejiService.isRunning) {
                triggerAction("files");
            }
        } catch (Exception e) {
            Toast.makeText(this, "Notas guardadas en almacenamiento de la app", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        updatePermissionUI();
        updateStatus();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_OVERLAY_PERMISSION) {
            updatePermissionUI();
            if (checkOverlayPermission()) {
                Toast.makeText(this, "Permiso concedido. Ya puedes usar los Shimejis", Toast.LENGTH_SHORT).show();
            }
        }
        if (requestCode == REQUEST_PICK_SKIN_ZIP && resultCode == RESULT_OK && data != null && data.getData() != null) {
            importSkinFromZip(data.getData());
        }
    }

    public int dpToPx(float dp) {
        float density = getResources().getDisplayMetrics().density;
        return (int) (dp * density + 0.5f);
    }

    private GradientDrawable createChipDrawable() {
        GradientDrawable gd = new GradientDrawable();
        gd.setShape(GradientDrawable.RECTANGLE);
        gd.setCornerRadius(dpToPx(14));
        gd.setColor(Color.parseColor("#261F38"));
        gd.setStroke(dpToPx(1), Color.parseColor("#3D3352"));
        return gd;
    }

    private GradientDrawable createEditTextDrawable() {
        GradientDrawable gd = new GradientDrawable();
        gd.setShape(GradientDrawable.RECTANGLE);
        gd.setCornerRadius(dpToPx(16));
        gd.setColor(Color.parseColor("#1B162B"));
        gd.setStroke(dpToPx(1), Color.parseColor("#3D3352"));
        return gd;
    }

    private GradientDrawable createButtonPillDrawable() {
        GradientDrawable gd = new GradientDrawable();
        gd.setShape(GradientDrawable.RECTANGLE);
        gd.setCornerRadius(dpToPx(18));
        gd.setColor(Color.parseColor("#8A56E2"));
        return gd;
    }

    private GradientDrawable createBubbleDrawable(boolean isUser) {
        GradientDrawable gd = new GradientDrawable();
        gd.setShape(GradientDrawable.RECTANGLE);
        gd.setCornerRadius(dpToPx(14));
        if (isUser) {
            gd.setColor(Color.parseColor("#8A56E2"));
        } else {
            gd.setColor(Color.parseColor("#221C34"));
            gd.setStroke(dpToPx(1), Color.parseColor("#3D3352"));
        }
        return gd;
    }

    private void addChatBubble(LinearLayout container, String text, boolean isUser) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(isUser ? Gravity.END : Gravity.START);
        LinearLayout.LayoutParams rowParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        rowParams.topMargin = dpToPx(4);
        rowParams.bottomMargin = dpToPx(4);
        row.setLayoutParams(rowParams);

        TextView tv = new TextView(this);
        tv.setText(text);
        tv.setTextColor(isUser ? Color.WHITE : Color.parseColor("#E6E1F0"));
        tv.setTextSize(12);
        tv.setBackground(createBubbleDrawable(isUser));
        tv.setPadding(dpToPx(12), dpToPx(8), dpToPx(12), dpToPx(8));
        tv.setMaxWidth(dpToPx(240));

        row.addView(tv);
        container.addView(row);
    }

    private void executeChatMessage(final LinearLayout container, String message, final Runnable onAdded) {
        addChatBubble(container, message, true);
        if (onAdded != null) onAdded.run();

        final String cmd = message.toLowerCase().trim();

        // 1. Ranuras de Comandos Prefabricados (ej: abrirapp-tiktok, ejecutarcomando-ls, decir-hola, etc. o agregar-...)
        boolean handledSlot = CommandSlotHelper.matchAndExecute(MainActivity.this, message, new CommandSlotHelper.ExecutionCallback() {
            @Override
            public void onExecuted(boolean success, final String reply) {
                container.post(new Runnable() {
                    @Override
                    public void run() {
                        addChatBubble(container, reply, false);
                        if (onAdded != null) onAdded.run();
                        if (ShimejiService.isRunning) {
                            Intent it = new Intent(MainActivity.this, ShimejiService.class);
                            it.setAction(ShimejiService.ACTION_TRIGGER);
                            it.putExtra(ShimejiService.EXTRA_TRIGGER_ACTION, "speech:" + reply);
                            startService(it);
                        }
                        refreshCommandSlotsUI();
                    }
                });
            }
        });
        if (handledSlot) {
            return;
        }

        // 2. Acciones fisicas y atajos del sistema
        if (cmd.contains("guitarra") || cmd.contains("toca")) {
            triggerAction("guitar");
            replyAndSpeak(container, "¡Solo de guitarra en vivo!", onAdded);
            return;
        } else if (cmd.contains("caja") || cmd.contains("escondete")) {
            triggerAction("box");
            replyAndSpeak(container, "¡Modo caja seguro activado!", onAdded);
            return;
        } else if (cmd.contains("baila") || cmd.contains("bailar")) {
            triggerAction("dance");
            replyAndSpeak(container, "¡Bailando! Siguiendo el ritmo.", onAdded);
            return;
        } else if (cmd.contains("item") || cmd.contains("comida") || cmd.contains("snack")) {
            if (ShimejiService.isRunning) {
                Intent it = new Intent(MainActivity.this, ShimejiService.class);
                it.setAction(ShimejiService.ACTION_DROP_ITEM);
                startService(it);
                replyAndSpeak(container, "¡Soltando snack para el Shimeji!", onAdded);
            } else {
                replyAndSpeak(container, "Inicia el Shimeji primero para soltar items.", onAdded);
            }
            return;
        } else if (cmd.contains("termux") || cmd.contains("consola") || cmd.contains("terminal")) {
            launchTermux();
            replyAndSpeak(container, "Lanzando Termux.", onAdded);
            return;
        } else if (cmd.contains("archivo") || cmd.contains("notas") || cmd.contains("carpeta")) {
            createDemoFilesAndFolders();
            replyAndSpeak(container, "Notas y carpeta creadas en Documents/Shijima.", onAdded);
            return;
        } else if (cmd.startsWith("abre ") || cmd.startsWith("abrir ") || cmd.startsWith("inicia ") || cmd.startsWith("iniciar ")) {
            String appQuery = cmd
                .replaceFirst("^(abre|abrir|inicia|iniciar)\\s+", "")
                .replace("la app de ", "")
                .replace("la aplicacion de ", "")
                .replace("el ", "")
                .replace("la ", "")
                .trim();
            String reply = launchAppByFilter(appQuery);
            replyAndSpeak(container, reply, onAdded);
            return;
        } else if (cmd.contains("hora") || cmd.contains("que hora es")) {
            java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("hh:mm a", java.util.Locale.getDefault());
            replyAndSpeak(container, "Son las " + sdf.format(new java.util.Date()) + ".", onAdded);
            return;
        }

        // 3. Consulta al motor de Inteligencia Artificial (Local Offline, Google Gemini o Cloud/Ollama)
        String savedSkin = prefs.getString(KEY_SKIN, "Konata");
        AiEngineHelper.askAi(MainActivity.this, savedSkin, message, new AiEngineHelper.AiCallback() {
            @Override
            public void onSuccess(final String reply) {
                replyAndSpeak(container, reply, onAdded);
            }

            @Override
            public void onError(final String errorMsg) {
                replyAndSpeak(container, errorMsg, onAdded);
            }
        });
    }

    private void replyAndSpeak(final LinearLayout container, final String reply, final Runnable onAdded) {
        container.postDelayed(new Runnable() {
            @Override
            public void run() {
                addChatBubble(container, reply, false);
                if (onAdded != null) onAdded.run();
                if (ShimejiService.isRunning) {
                    Intent it = new Intent(MainActivity.this, ShimejiService.class);
                    it.setAction(ShimejiService.ACTION_TRIGGER);
                    it.putExtra(ShimejiService.EXTRA_TRIGGER_ACTION, "speech:" + reply);
                    startService(it);
                }
            }
        }, 260);
    }

    private String launchAppByFilter(String query) {
        PackageManager pm = getPackageManager();
        Set<String> allowedSet = prefs.getStringSet(KEY_ALLOWED_APPS, null);

        if (query.equals("camara") || query.equals("fotos")) {
            Intent intent = new Intent(android.provider.MediaStore.INTENT_ACTION_STILL_IMAGE_CAMERA);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            if (intent.resolveActivity(pm) != null) {
                startActivity(intent);
                return "Abriendo la camara.";
            }
        }

        if (query.equals("ajustes") || query.equals("configuracion")) {
            Intent intent = new Intent(Settings.ACTION_SETTINGS);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
            return "Abriendo ajustes.";
        }

        List<ApplicationInfo> apps = pm.getInstalledApplications(PackageManager.GET_META_DATA);
        String cleanQuery = query.toLowerCase().replace(" ", "");

        ApplicationInfo bestMatch = null;
        for (ApplicationInfo app : apps) {
            String label = pm.getApplicationLabel(app).toString().toLowerCase();
            String cleanLabel = label.replace(" ", "");
            if (cleanLabel.equals(cleanQuery)) {
                bestMatch = app;
                break;
            } else if (cleanLabel.contains(cleanQuery) || cleanQuery.contains(cleanLabel)) {
                if (pm.getLaunchIntentForPackage(app.packageName) != null) {
                    bestMatch = app;
                }
            }
        }

        if (bestMatch != null) {
            String appLabel = pm.getApplicationLabel(bestMatch).toString();
            if (allowedSet != null && !allowedSet.contains(bestMatch.packageName)) {
                return "La app '" + appLabel + "' esta bloqueada en el filtro de apps.";
            }
            Intent launch = pm.getLaunchIntentForPackage(bestMatch.packageName);
            if (launch != null) {
                launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(launch);
                return "Abriendo " + appLabel + ".";
            }
        }

        return "No encontre la aplicacion '" + query + "'.";
    }

    private void showChatDialog() {
        final AlertDialog.Builder builder = new AlertDialog.Builder(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.parseColor("#120F1F"));
        root.setPadding(dpToPx(16), dpToPx(16), dpToPx(16), dpToPx(16));

        // Header
        LinearLayout header = new LinearLayout(this);
        header.setOrientation(LinearLayout.HORIZONTAL);
        header.setGravity(Gravity.CENTER_VERTICAL);
        header.setPadding(0, 0, 0, dpToPx(10));

        final String savedSkin = prefs.getString(KEY_SKIN, "Konata");
        final SkinData skinData = SkinData.get(savedSkin);

        ImageView ivAvatar = new ImageView(this);
        int avatarRes = R.drawable.ic_konata;
        if ("Bocchi".equalsIgnoreCase(savedSkin)) avatarRes = R.drawable.ic_bocchi;
        else if ("Monika".equalsIgnoreCase(savedSkin)) avatarRes = R.drawable.ic_monika;
        else if ("Natsuki".equalsIgnoreCase(savedSkin)) avatarRes = R.drawable.ic_natsuki;
        else if ("Sayori".equalsIgnoreCase(savedSkin)) avatarRes = R.drawable.ic_sayori;
        else if ("Yuri".equalsIgnoreCase(savedSkin)) avatarRes = R.drawable.ic_yuri;
        else if ("Hachi".equalsIgnoreCase(savedSkin)) avatarRes = R.drawable.ic_hachi;
        else if ("Usagi".equalsIgnoreCase(savedSkin)) avatarRes = R.drawable.ic_usagi;
        else if ("Pusheen".equalsIgnoreCase(savedSkin)) avatarRes = R.drawable.ic_pusheen;
        ivAvatar.setImageResource(avatarRes);
        LinearLayout.LayoutParams ivParams = new LinearLayout.LayoutParams(dpToPx(38), dpToPx(38));
        ivParams.rightMargin = dpToPx(10);
        header.addView(ivAvatar, ivParams);

        LinearLayout titleCol = new LinearLayout(this);
        titleCol.setOrientation(LinearLayout.VERTICAL);
        LinearLayout.LayoutParams titleColParams = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        titleCol.setLayoutParams(titleColParams);

        TextView tvName = new TextView(this);
        tvName.setText(skinData != null ? skinData.name : "Shimeji");
        tvName.setTextColor(Color.WHITE);
        tvName.setTextSize(15);
        tvName.setTypeface(null, android.graphics.Typeface.BOLD);
        titleCol.addView(tvName);

        TextView tvSub = new TextView(this);
        tvSub.setText(skinData != null ? skinData.tagline : "Compañero interactivo");
        tvSub.setTextColor(Color.parseColor("#B89FFF"));
        tvSub.setTextSize(11);
        titleCol.addView(tvSub);

        header.addView(titleCol);
        root.addView(header);

        // Barra de pestañas para SEPARAR la Inteligencia Artificial de los Diálogos Prefabricados
        LinearLayout tabsRow = new LinearLayout(this);
        tabsRow.setOrientation(LinearLayout.HORIZONTAL);
        tabsRow.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams tabsParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(36));
        tabsParams.bottomMargin = dpToPx(10);
        tabsRow.setLayoutParams(tabsParams);

        final Button btnTabAi = new Button(this);
        btnTabAi.setText("Chat con IA");
        btnTabAi.setTextSize(11);
        btnTabAi.setTypeface(null, android.graphics.Typeface.BOLD);
        btnTabAi.setTextColor(Color.WHITE);
        final GradientDrawable gdTabActive = new GradientDrawable();
        gdTabActive.setShape(GradientDrawable.RECTANGLE);
        gdTabActive.setCornerRadius(dpToPx(18));
        gdTabActive.setColor(Color.parseColor("#8A56E2"));
        btnTabAi.setBackground(gdTabActive);
        LinearLayout.LayoutParams tabLp1 = new LinearLayout.LayoutParams(0, dpToPx(36), 1f);
        tabLp1.rightMargin = dpToPx(4);
        btnTabAi.setLayoutParams(tabLp1);
        tabsRow.addView(btnTabAi);

        final Button btnTabPrefab = new Button(this);
        btnTabPrefab.setText("Diálogos del Personaje");
        btnTabPrefab.setTextSize(11);
        btnTabPrefab.setTypeface(null, android.graphics.Typeface.BOLD);
        btnTabPrefab.setTextColor(Color.parseColor("#B89FFF"));
        final GradientDrawable gdTabInactive = new GradientDrawable();
        gdTabInactive.setShape(GradientDrawable.RECTANGLE);
        gdTabInactive.setCornerRadius(dpToPx(18));
        gdTabInactive.setColor(Color.parseColor("#261F38"));
        gdTabInactive.setStroke(dpToPx(1), Color.parseColor("#3D3352"));
        btnTabPrefab.setBackground(gdTabInactive);
        LinearLayout.LayoutParams tabLp2 = new LinearLayout.LayoutParams(0, dpToPx(36), 1f);
        tabLp2.leftMargin = dpToPx(4);
        btnTabPrefab.setLayoutParams(tabLp2);
        tabsRow.addView(btnTabPrefab);

        root.addView(tabsRow);

        // SECCION 1: CHAT CON IA (Generativa: Gemini, Cloud u Offline)
        final LinearLayout layoutAiSection = new LinearLayout(this);
        layoutAiSection.setOrientation(LinearLayout.VERTICAL);

        // Indicador del motor IA activo
        String activeAiMode = prefs.getString(KEY_AI_MODE, "local");
        String aiEngineBadge = "Motor activo: Local Offline (Sin internet)";
        if ("gemini".equalsIgnoreCase(activeAiMode)) {
            String mName = prefs.getString(KEY_GEMINI_MODEL, "gemini-2.5-flash");
            aiEngineBadge = "Motor: Google Gemini API (" + mName + ")";
        } else if ("cloud".equalsIgnoreCase(activeAiMode)) {
            String cModel = prefs.getString(KEY_CLOUD_MODEL, "llama3");
            aiEngineBadge = "Motor: Cloud / Ollama (" + cModel + ")";
        }

        TextView tvAiEngineBadge = new TextView(this);
        tvAiEngineBadge.setText(aiEngineBadge);
        tvAiEngineBadge.setTextColor(Color.parseColor("#A382FF"));
        tvAiEngineBadge.setTextSize(10);
        tvAiEngineBadge.setPadding(dpToPx(6), 0, 0, dpToPx(6));
        layoutAiSection.addView(tvAiEngineBadge);

        final ScrollView svChat = new ScrollView(this);
        LinearLayout.LayoutParams svParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(210));
        svParams.bottomMargin = dpToPx(8);
        svChat.setLayoutParams(svParams);
        svChat.setBackgroundColor(Color.parseColor("#181428"));
        svChat.setPadding(dpToPx(10), dpToPx(10), dpToPx(10), dpToPx(10));

        final LinearLayout msgContainer = new LinearLayout(this);
        msgContainer.setOrientation(LinearLayout.VERTICAL);
        svChat.addView(msgContainer);
        layoutAiSection.addView(svChat);

        final Runnable scrollToBottom = new Runnable() {
            @Override
            public void run() {
                svChat.post(new Runnable() {
                    @Override
                    public void run() {
                        svChat.fullScroll(View.FOCUS_DOWN);
                    }
                });
            }
        };

        // Mensaje de bienvenida IA
        addChatBubble(msgContainer, "Hola, estoy lista para conversar contigo. Pregúntame lo que quieras.", false);

        // Chips de sugerencia para la IA
        HorizontalScrollView hsvChips = new HorizontalScrollView(this);
        hsvChips.setHorizontalScrollBarEnabled(false);
        LinearLayout.LayoutParams chipScrollParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        chipScrollParams.bottomMargin = dpToPx(8);
        hsvChips.setLayoutParams(chipScrollParams);

        LinearLayout chipsRow = new LinearLayout(this);
        chipsRow.setOrientation(LinearLayout.HORIZONTAL);
        hsvChips.addView(chipsRow);

        String[] quickChips = {"¿Quién eres?", "¿Cuál es tu historia?", "Cuéntame un secreto", "Bailar", "Guitarra", "Soltar item", "Termux", "Abre camara"};
        for (final String chipText : quickChips) {
            TextView chip = new TextView(this);
            chip.setText(chipText);
            chip.setTextColor(Color.parseColor("#E6E1F0"));
            chip.setTextSize(11);
            chip.setBackground(createChipDrawable());
            chip.setPadding(dpToPx(10), dpToPx(4), dpToPx(10), dpToPx(4));
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            lp.rightMargin = dpToPx(6);
            chip.setLayoutParams(lp);
            chip.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    executeChatMessage(msgContainer, chipText, scrollToBottom);
                }
            });
            chipsRow.addView(chip);
        }
        layoutAiSection.addView(hsvChips);

        // Fila de entrada de texto
        LinearLayout inputRow = new LinearLayout(this);
        inputRow.setOrientation(LinearLayout.HORIZONTAL);
        inputRow.setGravity(Gravity.CENTER_VERTICAL);

        final EditText etMessage = new EditText(this);
        etMessage.setHint("Escribe para la IA o un comando...");
        etMessage.setHintTextColor(Color.parseColor("#665D7E"));
        etMessage.setTextColor(Color.WHITE);
        etMessage.setTextSize(13);
        etMessage.setBackground(createEditTextDrawable());
        etMessage.setPadding(dpToPx(12), dpToPx(8), dpToPx(12), dpToPx(8));
        LinearLayout.LayoutParams etParams = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        etParams.rightMargin = dpToPx(8);
        inputRow.addView(etMessage, etParams);

        Button btnSend = new Button(this);
        btnSend.setText("Enviar");
        btnSend.setTextColor(Color.WHITE);
        btnSend.setTextSize(12);
        btnSend.setTypeface(null, android.graphics.Typeface.BOLD);
        btnSend.setBackground(createButtonPillDrawable());
        LinearLayout.LayoutParams btnParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT, dpToPx(38));
        inputRow.addView(btnSend, btnParams);
        layoutAiSection.addView(inputRow);

        root.addView(layoutAiSection);

        // SECCION 2: DIALOGOS PREFABRICADOS Y CITAS DEL PERSONAJE
        final LinearLayout layoutPrefabSection = new LinearLayout(this);
        layoutPrefabSection.setOrientation(LinearLayout.VERTICAL);
        layoutPrefabSection.setVisibility(View.GONE);

        TextView tvPrefabDesc = new TextView(this);
        tvPrefabDesc.setText("Repertorio de más de 40 frases y citas del personaje activo. Toca cualquiera para que el Shimeji la diga en pantalla:");
        tvPrefabDesc.setTextColor(Color.parseColor("#B89FFF"));
        tvPrefabDesc.setTextSize(11);
        tvPrefabDesc.setPadding(dpToPx(4), 0, 0, dpToPx(8));
        layoutPrefabSection.addView(tvPrefabDesc);

        // Botones de accion rápida para diálogos prefabricados
        LinearLayout prefabQuickRow = new LinearLayout(this);
        prefabQuickRow.setOrientation(LinearLayout.HORIZONTAL);
        prefabQuickRow.setPadding(0, 0, 0, dpToPx(8));

        Button btnRandomSpeech = new Button(this);
        btnRandomSpeech.setText("Frase Aleatoria");
        btnRandomSpeech.setTextColor(Color.WHITE);
        btnRandomSpeech.setTextSize(11);
        btnRandomSpeech.setTypeface(null, android.graphics.Typeface.BOLD);
        GradientDrawable gdRandom = new GradientDrawable();
        gdRandom.setShape(GradientDrawable.RECTANGLE);
        gdRandom.setCornerRadius(dpToPx(16));
        gdRandom.setColor(Color.parseColor("#8A56E2"));
        btnRandomSpeech.setBackground(gdRandom);
        LinearLayout.LayoutParams randLp = new LinearLayout.LayoutParams(0, dpToPx(34), 1f);
        randLp.rightMargin = dpToPx(4);
        btnRandomSpeech.setLayoutParams(randLp);
        prefabQuickRow.addView(btnRandomSpeech);

        Button btnRandomPoke = new Button(this);
        btnRandomPoke.setText("Frase al Tocar");
        btnRandomPoke.setTextColor(Color.WHITE);
        btnRandomPoke.setTextSize(11);
        btnRandomPoke.setTypeface(null, android.graphics.Typeface.BOLD);
        GradientDrawable gdPoke = new GradientDrawable();
        gdPoke.setShape(GradientDrawable.RECTANGLE);
        gdPoke.setCornerRadius(dpToPx(16));
        gdPoke.setColor(Color.parseColor("#372B52"));
        gdPoke.setStroke(dpToPx(1), Color.parseColor("#5A4580"));
        btnRandomPoke.setBackground(gdPoke);
        LinearLayout.LayoutParams pokeLp = new LinearLayout.LayoutParams(0, dpToPx(34), 1f);
        pokeLp.leftMargin = dpToPx(4);
        btnRandomPoke.setLayoutParams(pokeLp);
        prefabQuickRow.addView(btnRandomPoke);

        layoutPrefabSection.addView(prefabQuickRow);

        // Buscador de frases prefabricadas
        final EditText etFilterPrefab = new EditText(this);
        etFilterPrefab.setHint("Buscar en las frases prefabricadas...");
        etFilterPrefab.setHintTextColor(Color.parseColor("#665D7E"));
        etFilterPrefab.setTextColor(Color.WHITE);
        etFilterPrefab.setTextSize(12);
        etFilterPrefab.setBackground(createEditTextDrawable());
        etFilterPrefab.setPadding(dpToPx(12), dpToPx(6), dpToPx(12), dpToPx(6));
        LinearLayout.LayoutParams filterParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        filterParams.bottomMargin = dpToPx(8);
        etFilterPrefab.setLayoutParams(filterParams);
        layoutPrefabSection.addView(etFilterPrefab);

        // Contenedor scrollable de la lista de frases
        final ScrollView svPrefab = new ScrollView(this);
        LinearLayout.LayoutParams svPrefabParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(220));
        svPrefab.setLayoutParams(svPrefabParams);
        svPrefab.setBackgroundColor(Color.parseColor("#181428"));
        svPrefab.setPadding(dpToPx(8), dpToPx(8), dpToPx(8), dpToPx(8));

        final LinearLayout listPrefabContainer = new LinearLayout(this);
        listPrefabContainer.setOrientation(LinearLayout.VERTICAL);
        svPrefab.addView(listPrefabContainer);
        layoutPrefabSection.addView(svPrefab);

        // Funcion para poblar la lista de frases prefabricadas
        final Runnable populatePrefabList = new Runnable() {
            @Override
            public void run() {
                listPrefabContainer.removeAllViews();
                if (skinData == null || skinData.dialogues == null) return;

                String filter = etFilterPrefab.getText().toString().trim().toLowerCase();
                int count = 0;

                for (final String phrase : skinData.dialogues) {
                    if (!filter.isEmpty() && !phrase.toLowerCase().contains(filter)) {
                        continue;
                    }
                    count++;

                    LinearLayout card = new LinearLayout(MainActivity.this);
                    card.setOrientation(LinearLayout.HORIZONTAL);
                    card.setGravity(Gravity.CENTER_VERTICAL);
                    GradientDrawable cd = new GradientDrawable();
                    cd.setShape(GradientDrawable.RECTANGLE);
                    cd.setCornerRadius(dpToPx(10));
                    cd.setColor(Color.parseColor("#221C34"));
                    cd.setStroke(dpToPx(1), Color.parseColor("#342B4C"));
                    card.setBackground(cd);
                    card.setPadding(dpToPx(10), dpToPx(8), dpToPx(10), dpToPx(8));
                    LinearLayout.LayoutParams cardLp = new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                    cardLp.bottomMargin = dpToPx(6);
                    card.setLayoutParams(cardLp);

                    TextView tvPhrase = new TextView(MainActivity.this);
                    tvPhrase.setText(phrase);
                    tvPhrase.setTextColor(Color.parseColor("#E6E1F0"));
                    tvPhrase.setTextSize(12);
                    LinearLayout.LayoutParams textLp = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
                    textLp.rightMargin = dpToPx(6);
                    tvPhrase.setLayoutParams(textLp);
                    card.addView(tvPhrase);

                    TextView tvPlay = new TextView(MainActivity.this);
                    tvPlay.setText("Decir");
                    tvPlay.setTextColor(Color.parseColor("#B89FFF"));
                    tvPlay.setTextSize(10);
                    tvPlay.setTypeface(null, android.graphics.Typeface.BOLD);
                    tvPlay.setBackground(createChipDrawable());
                    tvPlay.setPadding(dpToPx(8), dpToPx(4), dpToPx(8), dpToPx(4));
                    card.addView(tvPlay);

                    card.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View v) {
                            if (ShimejiService.isRunning) {
                                Intent it = new Intent(MainActivity.this, ShimejiService.class);
                                it.setAction(ShimejiService.ACTION_TRIGGER);
                                it.putExtra(ShimejiService.EXTRA_TRIGGER_ACTION, "speech:" + phrase);
                                startService(it);
                            }
                            Toast.makeText(MainActivity.this, skinData.name + ": \"" + phrase + "\"", Toast.LENGTH_SHORT).show();
                        }
                    });

                    listPrefabContainer.addView(card);
                }

                if (count == 0) {
                    TextView tvEmpty = new TextView(MainActivity.this);
                    tvEmpty.setText("No se encontraron frases que coincidan con el filtro.");
                    tvEmpty.setTextColor(Color.parseColor("#665D7E"));
                    tvEmpty.setTextSize(11);
                    tvEmpty.setPadding(dpToPx(10), dpToPx(20), dpToPx(10), dpToPx(20));
                    tvEmpty.setGravity(Gravity.CENTER);
                    listPrefabContainer.addView(tvEmpty);
                }
            }
        };

        populatePrefabList.run();

        etFilterPrefab.addTextChangedListener(new android.text.TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                populatePrefabList.run();
            }
            @Override
            public void afterTextChanged(android.text.Editable s) {}
        });

        btnRandomSpeech.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (skinData != null && skinData.dialogues != null && skinData.dialogues.length > 0) {
                    int r = new java.util.Random().nextInt(skinData.dialogues.length);
                    String quote = skinData.dialogues[r];
                    if (ShimejiService.isRunning) {
                        Intent it = new Intent(MainActivity.this, ShimejiService.class);
                        it.setAction(ShimejiService.ACTION_TRIGGER);
                        it.putExtra(ShimejiService.EXTRA_TRIGGER_ACTION, "speech:" + quote);
                        startService(it);
                    }
                    Toast.makeText(MainActivity.this, skinData.name + ": \"" + quote + "\"", Toast.LENGTH_SHORT).show();
                }
            }
        });

        btnRandomPoke.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (skinData != null && skinData.poked != null && skinData.poked.length > 0) {
                    int r = new java.util.Random().nextInt(skinData.poked.length);
                    String pokeQuote = skinData.poked[r];
                    if (ShimejiService.isRunning) {
                        Intent it = new Intent(MainActivity.this, ShimejiService.class);
                        it.setAction(ShimejiService.ACTION_TRIGGER);
                        it.putExtra(ShimejiService.EXTRA_TRIGGER_ACTION, "speech:" + pokeQuote);
                        startService(it);
                    }
                    Toast.makeText(MainActivity.this, skinData.name + " (Poke): \"" + pokeQuote + "\"", Toast.LENGTH_SHORT).show();
                }
            }
        });

        root.addView(layoutPrefabSection);

        // Controladores de cambio de pestaña
        btnTabAi.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                layoutAiSection.setVisibility(View.VISIBLE);
                layoutPrefabSection.setVisibility(View.GONE);
                btnTabAi.setBackground(gdTabActive);
                btnTabAi.setTextColor(Color.WHITE);
                btnTabPrefab.setBackground(gdTabInactive);
                btnTabPrefab.setTextColor(Color.parseColor("#B89FFF"));
            }
        });

        btnTabPrefab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                layoutAiSection.setVisibility(View.GONE);
                layoutPrefabSection.setVisibility(View.VISIBLE);
                btnTabPrefab.setBackground(gdTabActive);
                btnTabPrefab.setTextColor(Color.WHITE);
                btnTabAi.setBackground(gdTabInactive);
                btnTabAi.setTextColor(Color.parseColor("#B89FFF"));
            }
        });

        builder.setView(root);
        final AlertDialog dialog = builder.create();

        btnSend.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String txt = etMessage.getText().toString().trim();
                if (!txt.isEmpty()) {
                    etMessage.setText("");
                    executeChatMessage(msgContainer, txt, scrollToBottom);
                }
            }
        });

        dialog.show();
        scrollToBottom.run();
    }

    private void showAppFilterDialog() {
        PackageManager pm = getPackageManager();
        List<ApplicationInfo> allApps = pm.getInstalledApplications(PackageManager.GET_META_DATA);
        final List<AppItem> list = new ArrayList<>();
        Set<String> savedAllowed = prefs.getStringSet(KEY_ALLOWED_APPS, null);

        for (ApplicationInfo ai : allApps) {
            if (pm.getLaunchIntentForPackage(ai.packageName) != null) {
                String label = pm.getApplicationLabel(ai).toString();
                boolean isAllowed = (savedAllowed == null) || savedAllowed.contains(ai.packageName);
                list.add(new AppItem(label, ai.packageName, isAllowed));
            }
        }
        Collections.sort(list, (a, b) -> a.label.compareToIgnoreCase(b.label));

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.parseColor("#120F1F"));
        root.setPadding(dpToPx(16), dpToPx(16), dpToPx(16), dpToPx(16));

        TextView tvTitle = new TextView(this);
        tvTitle.setText("Filtro de Aplicaciones (Voz & Chat)");
        tvTitle.setTextColor(Color.WHITE);
        tvTitle.setTextSize(16);
        tvTitle.setTypeface(null, android.graphics.Typeface.BOLD);
        tvTitle.setPadding(0, 0, 0, dpToPx(6));
        root.addView(tvTitle);

        TextView tvDesc = new TextView(this);
        tvDesc.setText("Marca las aplicaciones que el Shimeji tiene permiso de abrir por voz o chat:");
        tvDesc.setTextColor(Color.parseColor("#B89FFF"));
        tvDesc.setTextSize(11);
        tvDesc.setPadding(0, 0, 0, dpToPx(10));
        root.addView(tvDesc);

        LinearLayout toggleRow = new LinearLayout(this);
        toggleRow.setOrientation(LinearLayout.HORIZONTAL);
        toggleRow.setPadding(0, 0, 0, dpToPx(10));

        Button btnAll = new Button(this);
        btnAll.setText("Permitir Todas");
        btnAll.setTextColor(Color.WHITE);
        btnAll.setTextSize(11);
        btnAll.setBackground(createButtonPillDrawable());
        LinearLayout.LayoutParams btnAllParams = new LinearLayout.LayoutParams(0, dpToPx(36), 1f);
        btnAllParams.rightMargin = dpToPx(4);
        toggleRow.addView(btnAll, btnAllParams);

        Button btnNone = new Button(this);
        btnNone.setText("Bloquear Todas");
        btnNone.setTextColor(Color.parseColor("#E6E1F0"));
        btnNone.setTextSize(11);
        btnNone.setBackground(createChipDrawable());
        LinearLayout.LayoutParams btnNoneParams = new LinearLayout.LayoutParams(0, dpToPx(36), 1f);
        btnNoneParams.leftMargin = dpToPx(4);
        toggleRow.addView(btnNone, btnNoneParams);
        root.addView(toggleRow);

        ScrollView sv = new ScrollView(this);
        LinearLayout.LayoutParams svLp = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(280));
        svLp.bottomMargin = dpToPx(12);
        sv.setLayoutParams(svLp);

        final LinearLayout listContainer = new LinearLayout(this);
        listContainer.setOrientation(LinearLayout.VERTICAL);
        sv.addView(listContainer);
        root.addView(sv);

        final List<CheckBox> checkBoxes = new ArrayList<>();
        for (final AppItem item : list) {
            CheckBox cb = new CheckBox(this);
            cb.setText(item.label + "\n(" + item.packageName + ")");
            cb.setTextColor(Color.parseColor("#E6E1F0"));
            cb.setTextSize(12);
            cb.setChecked(item.allowed);
            cb.setOnCheckedChangeListener((buttonView, isChecked) -> item.allowed = isChecked);
            checkBoxes.add(cb);
            listContainer.addView(cb);
        }

        btnAll.setOnClickListener(v -> {
            for (CheckBox cb : checkBoxes) cb.setChecked(true);
        });
        btnNone.setOnClickListener(v -> {
            for (CheckBox cb : checkBoxes) cb.setChecked(false);
        });

        Button btnSave = new Button(this);
        btnSave.setText("Guardar Filtro de Apps");
        btnSave.setTextColor(Color.WHITE);
        btnSave.setTextSize(13);
        btnSave.setTypeface(null, android.graphics.Typeface.BOLD);
        btnSave.setBackground(createButtonPillDrawable());
        LinearLayout.LayoutParams saveParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(44));
        root.addView(btnSave, saveParams);

        builder.setView(root);
        final AlertDialog dialog = builder.create();

        btnSave.setOnClickListener(v -> {
            Set<String> newAllowed = new HashSet<>();
            int count = 0;
            for (AppItem itm : list) {
                if (itm.allowed) {
                    newAllowed.add(itm.packageName);
                    count++;
                }
            }
            prefs.edit().putStringSet(KEY_ALLOWED_APPS, newAllowed).apply();
            Toast.makeText(MainActivity.this, "Filtro guardado (" + count + " apps permitidas)", Toast.LENGTH_SHORT).show();
            dialog.dismiss();
        });

        dialog.show();
    }

    private void showCustomSizeDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.parseColor("#120F1F"));
        root.setPadding(dpToPx(16), dpToPx(16), dpToPx(16), dpToPx(16));

        TextView tvTitle = new TextView(this);
        tvTitle.setText("Tamaño Personalizable");
        tvTitle.setTextColor(Color.WHITE);
        tvTitle.setTextSize(16);
        tvTitle.setTypeface(null, android.graphics.Typeface.BOLD);
        tvTitle.setPadding(0, 0, 0, dpToPx(6));
        root.addView(tvTitle);

        TextView tvDesc = new TextView(this);
        tvDesc.setText("Ingresa el tamaño en dp o un multiplicador (ejemplo: 200, 300, 100x, 2x):");
        tvDesc.setTextColor(Color.parseColor("#B89FFF"));
        tvDesc.setTextSize(12);
        tvDesc.setPadding(0, 0, 0, dpToPx(10));
        root.addView(tvDesc);

        final EditText etSize = new EditText(this);
        int currentSize = prefs.getInt(KEY_SIZE, 128);
        etSize.setText(String.valueOf(currentSize));
        etSize.setTextColor(Color.WHITE);
        etSize.setTextSize(14);
        etSize.setBackground(createEditTextDrawable());
        etSize.setPadding(dpToPx(12), dpToPx(10), dpToPx(12), dpToPx(10));
        LinearLayout.LayoutParams etParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        etParams.bottomMargin = dpToPx(12);
        root.addView(etSize, etParams);

        LinearLayout presets = new LinearLayout(this);
        presets.setOrientation(LinearLayout.HORIZONTAL);
        presets.setPadding(0, 0, 0, dpToPx(14));

        String[] presetLabels = {"96", "128", "160", "250", "400", "100x"};
        for (final String pl : presetLabels) {
            TextView btnPreset = new TextView(this);
            btnPreset.setText(pl);
            btnPreset.setTextColor(Color.WHITE);
            btnPreset.setTextSize(11);
            btnPreset.setBackground(createChipDrawable());
            btnPreset.setPadding(dpToPx(10), dpToPx(6), dpToPx(10), dpToPx(6));
            LinearLayout.LayoutParams pLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            pLp.rightMargin = dpToPx(6);
            btnPreset.setLayoutParams(pLp);
            btnPreset.setOnClickListener(v -> etSize.setText(pl));
            presets.addView(btnPreset);
        }
        root.addView(presets);

        Button btnApply = new Button(this);
        btnApply.setText("Aplicar Tamaño");
        btnApply.setTextColor(Color.WHITE);
        btnApply.setTextSize(13);
        btnApply.setTypeface(null, android.graphics.Typeface.BOLD);
        btnApply.setBackground(createButtonPillDrawable());
        LinearLayout.LayoutParams applyLp = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(44));
        root.addView(btnApply, applyLp);

        builder.setView(root);
        final AlertDialog dialog = builder.create();

        btnApply.setOnClickListener(v -> {
            String val = etSize.getText().toString().trim().toLowerCase();
            int parsedDp = 128;
            try {
                if (val.endsWith("x")) {
                    float multiplier = Float.parseFloat(val.replace("x", ""));
                    parsedDp = (int) (128 * multiplier);
                } else if (val.endsWith("%")) {
                    float pct = Float.parseFloat(val.replace("%", ""));
                    parsedDp = (int) (128 * (pct / 100f));
                } else {
                    parsedDp = Integer.parseInt(val);
                }
            } catch (Exception e) {
                parsedDp = 128;
            }

            parsedDp = Math.max(32, Math.min(650, parsedDp));

            badgeSizeNum.setText(parsedDp + " dp");
            prefs.edit().putInt(KEY_SIZE, parsedDp).apply();

            if (ShimejiService.isRunning) {
                Intent intent = new Intent(MainActivity.this, ShimejiService.class);
                intent.setAction(ShimejiService.ACTION_SET_SIZE);
                intent.putExtra(ShimejiService.EXTRA_SIZE_DP, parsedDp);
                startService(intent);
            }
            Toast.makeText(MainActivity.this, "Tamaño actualizado a " + parsedDp + " dp", Toast.LENGTH_SHORT).show();
            dialog.dismiss();
        });

        dialog.show();
    }

    private void checkForUpdates(final boolean isManual) {
        ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo ni = cm != null ? cm.getActiveNetworkInfo() : null;
        boolean isConnected = (ni != null && ni.isConnected());

        if (!isConnected) {
            if (isManual) {
                Toast.makeText(this, "Sin conexion a internet para buscar actualizaciones.", Toast.LENGTH_SHORT).show();
            }
            return;
        }

        if (!isManual) {
            long lastCheck = prefs.getLong(KEY_LAST_UPDATE_CHECK, 0L);
            if (System.currentTimeMillis() - lastCheck < UPDATE_CHECK_INTERVAL_MS) {
                return;
            }
        }

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    URL url = new URL("https://raw.githubusercontent.com/MegatronF0id5la4yer/bocchi-shimeji-con-ia-local-y-api/main/version.json");
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setConnectTimeout(6000);
                    conn.setReadTimeout(6000);
                    conn.setRequestMethod("GET");
                    conn.connect();

                    if (conn.getResponseCode() == 200) {
                        BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                        StringBuilder sb = new StringBuilder();
                        String line;
                        while ((line = reader.readLine()) != null) {
                            sb.append(line);
                        }
                        reader.close();
                        conn.disconnect();

                        JSONObject json = new JSONObject(sb.toString());
                        final int remoteVersionCode = json.optInt("versionCode", 1);
                        final String remoteVersionName = json.optString("versionName", "1.0");
                        final String apkUrl = json.optString("apkUrl", "");
                        JSONArray featuresArray = json.optJSONArray("features");
                        final StringBuilder featuresText = new StringBuilder();
                        if (featuresArray != null) {
                            for (int i = 0; i < featuresArray.length(); i++) {
                                featuresText.append("• ").append(featuresArray.getString(i)).append("\n");
                            }
                        }

                        int currentCode = 3;
                        try {
                            PackageInfo pInfo = getPackageManager().getPackageInfo(getPackageName(), 0);
                            currentCode = pInfo.versionCode;
                        } catch (Exception ignored) {}

                        final int curCode = currentCode;
                        prefs.edit().putLong(KEY_LAST_UPDATE_CHECK, System.currentTimeMillis()).apply();

                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                if (remoteVersionCode > curCode) {
                                    showUpdateDialog(remoteVersionName, featuresText.toString(), apkUrl);
                                } else if (isManual) {
                                    Toast.makeText(MainActivity.this, "Tienes la version mas reciente (v" + remoteVersionName + ")", Toast.LENGTH_LONG).show();
                                }
                            }
                        });
                    }
                } catch (Exception e) {
                    if (isManual) {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                Toast.makeText(MainActivity.this, "No se pudo verificar la actualizacion en este momento.", Toast.LENGTH_SHORT).show();
                            }
                        });
                    }
                }
            }
        }).start();
    }

    private void showUpdateDialog(final String versionName, final String features, final String apkUrl) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Nueva Actualizacion (v" + versionName + ")");
        builder.setMessage("Se ha encontrado una nueva version con mejoras:\n\n" + features + "\n¿Deseas descargar e instalar ahora?");
        builder.setPositiveButton("Descargar APK", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                try {
                    DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                    Uri uri = Uri.parse(apkUrl);
                    DownloadManager.Request request = new DownloadManager.Request(uri);
                    request.setTitle("PinkChan Shimeji v" + versionName);
                    request.setDescription("Descargando actualizacion oficial...");
                    request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                    request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "PinkChan_Shimeji_v" + versionName + ".apk");
                    if (dm != null) {
                        dm.enqueue(request);
                        Toast.makeText(MainActivity.this, "Descarga iniciada. Revisa tus notificaciones.", Toast.LENGTH_LONG).show();
                    }
                } catch (Exception e) {
                    try {
                        Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(apkUrl));
                        startActivity(browserIntent);
                    } catch (Exception ignored) {}
                }
            }
        });
        builder.setNegativeButton("Mas tarde", null);
        builder.show();
    }

    private void loadPrebuiltMacros() {
        try {
            String cur = prefs.getString(AgentToolExecutor.PREF_MACROS, "{}");
            JSONObject o = new JSONObject(cur);

            // 1. modo estudio
            JSONArray mEstudio = new JSONArray();
            mEstudio.put("[JARVIS: VOLUME 25]");
            mEstudio.put("WAIT 1");
            mEstudio.put("[JARVIS: SEARCH_YT \"lofi hip hop radio live\"]");
            mEstudio.put("WAIT 1");
            mEstudio.put("[JARVIS: REMIND 25m \"Pomodoro: descanso de 5 min\"]");
            o.put("modo estudio", mEstudio);

            // 2. modo gamer
            JSONArray mGamer = new JSONArray();
            mGamer.put("[JARVIS: VOLUME 80]");
            mGamer.put("WAIT 1");
            mGamer.put("[JARVIS: BRIGHTNESS 100]");
            mGamer.put("WAIT 1");
            mGamer.put("[JARVIS: OPEN \"discord\"]");
            o.put("modo gamer", mGamer);

            // 3. buenas noches
            JSONArray mNoches = new JSONArray();
            mNoches.put("[JARVIS: VOLUME 10]");
            mNoches.put("WAIT 1");
            mNoches.put("[JARVIS: BRIGHTNESS 15]");
            mNoches.put("WAIT 1");
            mNoches.put("[JARVIS: REMIND 480m \"Buenos dias! Hora de levantarse\"]");
            mNoches.put("WAIT 1");
            mNoches.put("[JARVIS: LOCK]");
            o.put("buenas noches", mNoches);

            // 4. diagnostico
            JSONArray mDiag = new JSONArray();
            mDiag.put("[JARVIS: LIST \"Shijima\"]");
            mDiag.put("WAIT 1");
            mDiag.put("[JARVIS: BATTERY]");
            o.put("diagnostico", mDiag);

            // 5. silencio total
            JSONArray mSilencio = new JSONArray();
            mSilencio.put("[JARVIS: VOLUME 0]");
            mSilencio.put("WAIT 1");
            mSilencio.put("[JARVIS: SCREENSHOT]");
            o.put("silencio total", mSilencio);

            prefs.edit().putString(AgentToolExecutor.PREF_MACROS, o.toString()).apply();
            refreshMacrosUI();
            Toast.makeText(this, "Se cargaron 5 macros predeterminadas con exito", Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            Toast.makeText(this, "Error al cargar macros: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private void importSkinFromZip(final Uri uri) {
        if (uri == null) return;
        Toast.makeText(this, "Procesando e importando archivo ZIP...", Toast.LENGTH_SHORT).show();

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    String baseName = "CustomSkin";
                    Cursor cursor = getContentResolver().query(uri, null, null, null, null);
                    if (cursor != null) {
                        try {
                            if (cursor.moveToFirst()) {
                                int nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                                if (nameIndex >= 0) {
                                    String displayName = cursor.getString(nameIndex);
                                    if (displayName != null && !displayName.isEmpty()) {
                                        baseName = displayName;
                                    }
                                }
                            }
                        } finally {
                            cursor.close();
                        }
                    }

                    if (baseName.toLowerCase().endsWith(".zip")) {
                        baseName = baseName.substring(0, baseName.length() - 4);
                    }
                    String cleanName = baseName.replaceAll("[^a-zA-Z0-9_\\-]", "_");
                    if (cleanName.isEmpty()) cleanName = "SkinImportada";
                    cleanName = Character.toUpperCase(cleanName.charAt(0)) + (cleanName.length() > 1 ? cleanName.substring(1) : "");

                    File customDir = SkinData.getCustomSkinsDir(MainActivity.this);
                    File skinDir = new File(customDir, cleanName);
                    if (!skinDir.exists()) {
                        skinDir.mkdirs();
                    }

                    InputStream is = getContentResolver().openInputStream(uri);
                    if (is == null) {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                Toast.makeText(MainActivity.this, "No se pudo abrir el archivo ZIP seleccionado", Toast.LENGTH_LONG).show();
                            }
                        });
                        return;
                    }

                    ZipInputStream zis = new ZipInputStream(new BufferedInputStream(is));
                    ZipEntry entry;
                    byte[] buffer = new byte[8192];
                    int frameCount = 0;

                    while ((entry = zis.getNextEntry()) != null) {
                        if (entry.isDirectory()) {
                            zis.closeEntry();
                            continue;
                        }

                        String rawName = new File(entry.getName()).getName();
                        if (rawName == null || rawName.isEmpty()) {
                            zis.closeEntry();
                            continue;
                        }

                        String lower = rawName.toLowerCase();
                        if (lower.endsWith(".png") || lower.endsWith(".xml")) {
                            File outFile = new File(skinDir, rawName);
                            FileOutputStream fos = new FileOutputStream(outFile);
                            int len;
                            while ((len = zis.read(buffer)) > 0) {
                                fos.write(buffer, 0, len);
                            }
                            fos.close();

                            // Normalizacion: si es 1.png -> tambien guardar como shime1.png
                            if (lower.matches("^\\d+\\.png$")) {
                                String numPart = lower.replace(".png", "");
                                File shimeAlias = new File(skinDir, "shime" + numPart + ".png");
                                if (!shimeAlias.exists()) {
                                    copyFile(outFile, shimeAlias);
                                }
                            } else if (lower.matches("^shime\\d+\\.png$")) {
                                String numPart = lower.replace("shime", "").replace(".png", "");
                                File simpleAlias = new File(skinDir, numPart + ".png");
                                if (!simpleAlias.exists()) {
                                    copyFile(outFile, simpleAlias);
                                }
                            }

                            if (lower.endsWith(".png")) {
                                frameCount++;
                            }
                        }
                        zis.closeEntry();
                    }
                    zis.close();
                    is.close();

                    final int totalFrames = frameCount;
                    final String finalSkinName = cleanName;

                    SkinData.registerCustomSkin(MainActivity.this, finalSkinName);
                    SkinData.loadCustomSkins(MainActivity.this);

                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            if (totalFrames > 0) {
                                AlertDialog.Builder b = new AlertDialog.Builder(MainActivity.this);
                                b.setTitle("Skin Importada: " + finalSkinName);
                                b.setMessage("Se extrajeron " + totalFrames + " frames de sprites correctamente.\n¿Deseas activar esta skin ahora en pantalla?");
                                b.setPositiveButton("Activar Ahora", new DialogInterface.OnClickListener() {
                                    @Override
                                    public void onClick(DialogInterface d, int w) {
                                        spawnOrSelectSkin(finalSkinName);
                                    }
                                });
                                b.setNegativeButton("Mas tarde", null);
                                b.show();
                            } else {
                                Toast.makeText(MainActivity.this, "El ZIP no contenia imagenes .png validas", Toast.LENGTH_LONG).show();
                            }
                        }
                    });

                } catch (final Exception e) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Toast.makeText(MainActivity.this, "Error importando skin: " + e.getMessage(), Toast.LENGTH_LONG).show();
                        }
                    });
                }
            }
        }).start();
    }

    private static void copyFile(File src, File dst) {
        try {
            FileInputStream in = new FileInputStream(src);
            FileOutputStream out = new FileOutputStream(dst);
            byte[] buf = new byte[4096];
            int len;
            while ((len = in.read(buf)) > 0) {
                out.write(buf, 0, len);
            }
            in.close();
            out.close();
        } catch (Exception ignored) {}
    }

    private static class AppItem {
        final String label;
        final String packageName;
        boolean allowed;
        AppItem(String label, String packageName, boolean allowed) {
            this.label = label;
            this.packageName = packageName;
            this.allowed = allowed;
        }
    }
}

