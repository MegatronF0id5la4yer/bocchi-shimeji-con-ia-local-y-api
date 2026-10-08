package com.bocchi.pinkchan.shimeji;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {

    private static final int REQUEST_OVERLAY_PERMISSION = 2001;
    private static final int REQUEST_RECORD_AUDIO_PERMISSION = 2002;

    private static final String PREFS_NAME = "pinkchan_shimeji_prefs";
    private static final String KEY_SKIN = "selected_skin";
    private static final String KEY_SIZE = "selected_size";
    private static final String KEY_ZERO_G = "zero_gravity";

    // 4 Screens & Tabs
    private TextView tabFeatured, tabInstalled, tabInspector, tabSettings;
    private View screenFeatured, screenInstalled, screenInspector, screenSettings;

    // Screen 1: Featured
    private TextView btnGridCompact, btnGridStandard, btnGridWide;
    private TextView tvActiveOverlayCount;
    private Button btnSpawnKonata, btnSpawnBocchi, btnSpawnMonika, btnSpawnNatsuki, btnSpawnSayori, btnSpawnYuri;

    // Screen 2: Installed
    private View btnActionImport, btnActionGuide;
    private Button btnListSpawnKonata, btnListSpawnBocchi, btnListSpawnMonika, btnAddCategories;

    // Screen 3: Inspector
    private TextView tvInspectorStatus;
    private Button btnSpawnCustom, btnInteractionButton, btnCustomizeViews, btnInspectorVoice;
    private Button btnInspectorGuitar, btnInspectorBox, btnInspectorCenter;

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

        // Featured views
        tvActiveOverlayCount = findViewById(R.id.tv_active_overlay_count);
        btnGridCompact = findViewById(R.id.btn_grid_compact);
        btnGridStandard = findViewById(R.id.btn_grid_standard);
        btnGridWide = findViewById(R.id.btn_grid_wide);

        btnSpawnKonata = findViewById(R.id.btn_spawn_konata);
        btnSpawnBocchi = findViewById(R.id.btn_spawn_bocchi);
        btnSpawnMonika = findViewById(R.id.btn_spawn_monika);
        btnSpawnNatsuki = findViewById(R.id.btn_spawn_natsuki);
        btnSpawnSayori = findViewById(R.id.btn_spawn_sayori);
        btnSpawnYuri = findViewById(R.id.btn_spawn_yuri);

        // Installed views
        btnActionImport = findViewById(R.id.btn_action_import);
        btnActionGuide = findViewById(R.id.btn_action_guide);
        btnListSpawnKonata = findViewById(R.id.btn_list_spawn_konata);
        btnListSpawnBocchi = findViewById(R.id.btn_list_spawn_bocchi);
        btnListSpawnMonika = findViewById(R.id.btn_list_spawn_monika);
        btnAddCategories = findViewById(R.id.btn_add_categories);

        // Inspector views
        tvInspectorStatus = findViewById(R.id.tv_inspector_status);
        btnSpawnCustom = findViewById(R.id.btn_spawn_custom);
        btnInteractionButton = findViewById(R.id.btn_interaction_button);
        btnCustomizeViews = findViewById(R.id.btn_customize_views);
        btnInspectorVoice = findViewById(R.id.btn_inspector_voice);
        btnInspectorGuitar = findViewById(R.id.btn_inspector_guitar);
        btnInspectorBox = findViewById(R.id.btn_inspector_box);
        btnInspectorCenter = findViewById(R.id.btn_inspector_center);

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
        tabFeatured.setBackgroundResource(index == 0 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        tabFeatured.setTextColor(getResources().getColor(index == 0 ? R.color.accent_lavender_light : R.color.text_secondary));

        tabInstalled.setBackgroundResource(index == 1 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        tabInstalled.setTextColor(getResources().getColor(index == 1 ? R.color.accent_lavender_light : R.color.text_secondary));

        tabInspector.setBackgroundResource(index == 2 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        tabInspector.setTextColor(getResources().getColor(index == 2 ? R.color.accent_lavender_light : R.color.text_secondary));

        tabSettings.setBackgroundResource(index == 3 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        tabSettings.setTextColor(getResources().getColor(index == 3 ? R.color.accent_lavender_light : R.color.text_secondary));

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

        // Spawn handlers for 6 characters
        btnSpawnKonata.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Konata");
            }
        });
        btnSpawnBocchi.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Bocchi");
            }
        });
        btnSpawnMonika.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Monika");
            }
        });
        btnSpawnNatsuki.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Natsuki");
            }
        });
        btnSpawnSayori.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Sayori");
            }
        });
        btnSpawnYuri.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                spawnOrSelectSkin("Yuri");
            }
        });
    }

    private void setGridSizeTab(int idx) {
        btnGridCompact.setBackgroundResource(idx == 0 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        btnGridCompact.setTextColor(getResources().getColor(idx == 0 ? R.color.accent_lavender_light : R.color.text_secondary));

        btnGridStandard.setBackgroundResource(idx == 1 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        btnGridStandard.setTextColor(getResources().getColor(idx == 1 ? R.color.accent_lavender_light : R.color.text_secondary));

        btnGridWide.setBackgroundResource(idx == 2 ? R.drawable.tab_item_selected : R.drawable.tab_item_unselected);
        btnGridWide.setTextColor(getResources().getColor(idx == 2 ? R.color.accent_lavender_light : R.color.text_secondary));
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
                    startShimejiWithSkin("Konata");
                }
            }
        });

        btnInteractionButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerAction("pet");
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
    }

    private void spawnOrSelectSkin(String skinId) {
        if (!checkOverlayPermission()) {
            Toast.makeText(this, "Concede el permiso de superposicion primero", Toast.LENGTH_LONG).show();
            requestOverlayPermission();
            return;
        }

        prefs.edit().putString(KEY_SKIN, skinId).apply();

        if (ShimejiService.isRunning) {
            Intent intent = new Intent(this, ShimejiService.class);
            intent.setAction(ShimejiService.ACTION_ADD_SHIMEJI);
            intent.putExtra(ShimejiService.EXTRA_SKIN, skinId);
            startService(intent);
            Toast.makeText(this, skinId + " invocado en pantalla", Toast.LENGTH_SHORT).show();
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

