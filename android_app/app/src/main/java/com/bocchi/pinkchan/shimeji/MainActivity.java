package com.bocchi.pinkchan.shimeji;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.res.ColorStateList;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.ImageView;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {

    private static final int REQUEST_OVERLAY_PERMISSION = 2001;
    private static final int REQUEST_RECORD_AUDIO_PERMISSION = 2002;

    public static final String PREFS_NAME = "pinkchan_shimeji_prefs";
    public static final String KEY_SKIN = "selected_skin";
    public static final String KEY_SIZE = "selected_size";
    public static final String KEY_ZERO_G = "zero_gravity";
    public static final String KEY_ACCENT_INDEX = "selected_accent_index";

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
    private Button btnSpawnCustom, btnInteractionButton, btnCustomizeViews, btnInspectorVoice;
    private Button btnInspectorGuitar, btnInspectorBox, btnInspectorCenter;
    private Button btnInspectorPlay, btnInspectorDance, btnInspectorTermux, btnInspectorFiles;

    // Screen 4: Settings
    private TextView badgeSizeNum;
    private RadioGroup rgSettingsSize;
    private CheckBox cbSettingsZeroG;
    private Button btnSettingsPermission;
    private Button btnSettingsAppFilter;
    private Button btnSettingsClearExtras;
    private Button btnSettingsStop;

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
        cbSettingsZeroG = findViewById(R.id.cb_settings_zerog);
        btnSettingsPermission = findViewById(R.id.btn_settings_permission);
        btnSettingsAppFilter = findViewById(R.id.btn_settings_app_filter);
        btnSettingsClearExtras = findViewById(R.id.btn_settings_clear_extras);
        btnSettingsStop = findViewById(R.id.btn_settings_stop);
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

        btnSettingsPermission.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                requestOverlayPermission();
            }
        });

        btnSettingsAppFilter.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(MainActivity.this, "Filtro de aplicaciones activas configurado", Toast.LENGTH_SHORT).show();
            }
        });

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
}

