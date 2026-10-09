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

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.json.JSONArray;
import org.json.JSONObject;

public class MainActivity extends Activity {

    private static final int REQUEST_OVERLAY_PERMISSION = 2001;
    private static final int REQUEST_RECORD_AUDIO_PERMISSION = 2002;

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
        String reply;

        if (cmd.contains("hola") || cmd.contains("buenos dias") || cmd.contains("que tal")) {
            String savedSkin = prefs.getString(KEY_SKIN, "Konata");
            SkinData sd = SkinData.get(savedSkin);
            reply = (sd != null) ? sd.greeting : "¡Hola! Estoy aqui contigo.";
        } else if (cmd.contains("guitarra") || cmd.contains("toca")) {
            triggerAction("guitar");
            reply = "¡Solo de guitarra en vivo!";
        } else if (cmd.contains("caja") || cmd.contains("escondete")) {
            triggerAction("box");
            reply = "¡Modo caja seguro activado!";
        } else if (cmd.contains("baila") || cmd.contains("bailar")) {
            triggerAction("dance");
            reply = "¡Bailando! Siguiendo el ritmo.";
        } else if (cmd.contains("item") || cmd.contains("comida") || cmd.contains("snack")) {
            if (ShimejiService.isRunning) {
                Intent it = new Intent(MainActivity.this, ShimejiService.class);
                it.setAction(ShimejiService.ACTION_DROP_ITEM);
                startService(it);
                reply = "¡Soltando snack para el Shimeji!";
            } else {
                reply = "Inicia el Shimeji primero para soltar items.";
            }
        } else if (cmd.contains("termux") || cmd.contains("consola") || cmd.contains("terminal")) {
            launchTermux();
            reply = "Lanzando Termux.";
        } else if (cmd.contains("archivo") || cmd.contains("notas") || cmd.contains("carpeta")) {
            createDemoFilesAndFolders();
            reply = "Notas y carpeta creadas en Documents/Shijima.";
        } else if (cmd.startsWith("abre ") || cmd.startsWith("abrir ") || cmd.startsWith("inicia ") || cmd.startsWith("iniciar ")) {
            String appQuery = cmd
                .replaceFirst("^(abre|abrir|inicia|iniciar)\\s+", "")
                .replace("la app de ", "")
                .replace("la aplicacion de ", "")
                .replace("el ", "")
                .replace("la ", "")
                .trim();
            reply = launchAppByFilter(appQuery);
        } else if (cmd.contains("hora") || cmd.contains("que hora es")) {
            java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("hh:mm a", java.util.Locale.getDefault());
            reply = "Son las " + sdf.format(new java.util.Date()) + ".";
        } else {
            String savedSkin = prefs.getString(KEY_SKIN, "Konata");
            SkinData sd = SkinData.get(savedSkin);
            if (sd != null && sd.speeches.length > 0) {
                reply = sd.speeches[new java.util.Random().nextInt(sd.speeches.length)];
            } else {
                reply = "Entendido: '" + message + "'.";
            }
        }

        final String finalReply = reply;
        container.postDelayed(new Runnable() {
            @Override
            public void run() {
                addChatBubble(container, finalReply, false);
                if (onAdded != null) onAdded.run();
                if (ShimejiService.isRunning) {
                    Intent it = new Intent(MainActivity.this, ShimejiService.class);
                    it.setAction(ShimejiService.ACTION_TRIGGER);
                    it.putExtra(ShimejiService.EXTRA_TRIGGER_ACTION, "speech:" + finalReply);
                    startService(it);
                }
            }
        }, 280);
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
        header.setPadding(0, 0, 0, dpToPx(12));

        String savedSkin = prefs.getString(KEY_SKIN, "Konata");
        SkinData skinData = SkinData.get(savedSkin);

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
        LinearLayout.LayoutParams ivParams = new LinearLayout.LayoutParams(dpToPx(40), dpToPx(40));
        ivParams.rightMargin = dpToPx(10);
        header.addView(ivAvatar, ivParams);

        LinearLayout titleCol = new LinearLayout(this);
        titleCol.setOrientation(LinearLayout.VERTICAL);
        LinearLayout.LayoutParams titleColParams = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        titleCol.setLayoutParams(titleColParams);

        TextView tvName = new TextView(this);
        tvName.setText(skinData != null ? skinData.name : "Shimeji");
        tvName.setTextColor(Color.WHITE);
        tvName.setTextSize(16);
        tvName.setTypeface(null, android.graphics.Typeface.BOLD);
        titleCol.addView(tvName);

        TextView tvSub = new TextView(this);
        tvSub.setText(skinData != null ? skinData.tagline : "Compañero interactivo");
        tvSub.setTextColor(Color.parseColor("#B89FFF"));
        tvSub.setTextSize(11);
        titleCol.addView(tvSub);

        header.addView(titleCol);
        root.addView(header);

        // Chat Message Log
        final ScrollView svChat = new ScrollView(this);
        LinearLayout.LayoutParams svParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dpToPx(240));
        svParams.bottomMargin = dpToPx(8);
        svChat.setLayoutParams(svParams);
        svChat.setBackgroundColor(Color.parseColor("#181428"));
        svChat.setPadding(dpToPx(10), dpToPx(10), dpToPx(10), dpToPx(10));

        final LinearLayout msgContainer = new LinearLayout(this);
        msgContainer.setOrientation(LinearLayout.VERTICAL);
        svChat.addView(msgContainer);
        root.addView(svChat);

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

        // Welcome message
        addChatBubble(msgContainer, skinData != null ? skinData.greeting : "¡Hola! ¿En que puedo ayudarte hoy?", false);

        // Quick suggestion chips
        HorizontalScrollView hsvChips = new HorizontalScrollView(this);
        hsvChips.setHorizontalScrollBarEnabled(false);
        LinearLayout.LayoutParams chipScrollParams = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        chipScrollParams.bottomMargin = dpToPx(10);
        hsvChips.setLayoutParams(chipScrollParams);

        LinearLayout chipsRow = new LinearLayout(this);
        chipsRow.setOrientation(LinearLayout.HORIZONTAL);
        hsvChips.addView(chipsRow);

        String[] quickChips = {"Hola", "Bailar", "Guitarra", "Caja", "Soltar item", "Termux", "Crear notas", "Abre camara"};
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
        root.addView(hsvChips);

        // Input row
        LinearLayout inputRow = new LinearLayout(this);
        inputRow.setOrientation(LinearLayout.HORIZONTAL);
        inputRow.setGravity(Gravity.CENTER_VERTICAL);

        final EditText etMessage = new EditText(this);
        etMessage.setHint("Escribe un mensaje o comando...");
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
            ViewGroup.LayoutParams.WRAP_CONTENT, dpToPx(40));
        inputRow.addView(btnSend, btnParams);
        root.addView(inputRow);

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

