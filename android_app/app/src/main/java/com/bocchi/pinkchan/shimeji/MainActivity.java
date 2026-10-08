package com.bocchi.pinkchan.shimeji;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
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
    private static final String PREFS_NAME = "pinkchan_shimeji_prefs";
    private static final String KEY_SKIN = "selected_skin";
    private static final String KEY_SIZE = "selected_size";
    private static final String KEY_ZERO_G = "zero_gravity";

    private TextView tvPermissionStatus;
    private Button btnGrantPermission;
    private Button btnStart;
    private Button btnStop;
    private Button btnCenter;
    private RadioGroup rgSkins;
    private RadioGroup rgSize;
    private CheckBox cbZeroGravity;

    private Button btnGuitar;
    private Button btnBox;
    private Button btnTalk;

    private SharedPreferences prefs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);

        initViews();
        setupListeners();
        restoreSavedPreferences();
    }

    private void initViews() {
        tvPermissionStatus = findViewById(R.id.tv_permission_status);
        btnGrantPermission = findViewById(R.id.btn_grant_permission);
        btnStart = findViewById(R.id.btn_start_shimeji);
        btnStop = findViewById(R.id.btn_stop_shimeji);
        btnCenter = findViewById(R.id.btn_center_shimeji);
        rgSkins = findViewById(R.id.rg_skins);
        rgSize = findViewById(R.id.rg_size);
        cbZeroGravity = findViewById(R.id.cb_zero_gravity);

        btnGuitar = findViewById(R.id.btn_action_guitar);
        btnBox = findViewById(R.id.btn_action_box);
        btnTalk = findViewById(R.id.btn_action_talk);
    }

    private void setupListeners() {
        btnGrantPermission.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                requestOverlayPermission();
            }
        });

        btnStart.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startShimeji();
            }
        });

        btnStop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopShimeji();
            }
        });

        btnCenter.setOnClickListener(new View.OnClickListener() {
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

        rgSkins.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(RadioGroup group, int checkedId) {
                String skin = getSelectedSkin();
                prefs.edit().putString(KEY_SKIN, skin).apply();

                if (ShimejiService.isRunning) {
                    Intent intent = new Intent(MainActivity.this, ShimejiService.class);
                    intent.setAction(ShimejiService.ACTION_SET_SKIN);
                    intent.putExtra(ShimejiService.EXTRA_SKIN, skin);
                    startService(intent);
                }
            }
        });

        rgSize.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(RadioGroup group, int checkedId) {
                int sizeDp = getSelectedSizeDp();
                prefs.edit().putInt(KEY_SIZE, sizeDp).apply();

                if (ShimejiService.isRunning) {
                    Intent intent = new Intent(MainActivity.this, ShimejiService.class);
                    intent.setAction(ShimejiService.ACTION_SET_SIZE);
                    intent.putExtra(ShimejiService.EXTRA_SIZE_DP, sizeDp);
                    startService(intent);
                }
            }
        });

        cbZeroGravity.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
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

        btnGuitar.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerAction("guitar");
            }
        });

        btnBox.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerAction("box");
            }
        });

        btnTalk.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                triggerAction("talk");
            }
        });
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

    private void restoreSavedPreferences() {
        String savedSkin = prefs.getString(KEY_SKIN, "Konata");
        if ("Bocchi".equals(savedSkin)) {
            ((RadioButton) findViewById(R.id.rb_bocchi)).setChecked(true);
        } else if ("Monika".equals(savedSkin)) {
            ((RadioButton) findViewById(R.id.rb_monika)).setChecked(true);
        } else if ("Natsuki".equals(savedSkin)) {
            ((RadioButton) findViewById(R.id.rb_natsuki)).setChecked(true);
        } else if ("Sayori".equals(savedSkin)) {
            ((RadioButton) findViewById(R.id.rb_sayori)).setChecked(true);
        } else if ("Yuri".equals(savedSkin)) {
            ((RadioButton) findViewById(R.id.rb_yuri)).setChecked(true);
        } else {
            ((RadioButton) findViewById(R.id.rb_konata)).setChecked(true);
        }

        int savedSize = prefs.getInt(KEY_SIZE, 128);
        if (savedSize == 96) {
            ((RadioButton) findViewById(R.id.rb_size_small)).setChecked(true);
        } else if (savedSize == 160) {
            ((RadioButton) findViewById(R.id.rb_size_large)).setChecked(true);
        } else {
            ((RadioButton) findViewById(R.id.rb_size_normal)).setChecked(true);
        }

        cbZeroGravity.setChecked(prefs.getBoolean(KEY_ZERO_G, false));
    }

    private String getSelectedSkin() {
        int checkedId = rgSkins.getCheckedRadioButtonId();
        if (checkedId == R.id.rb_bocchi) return "Bocchi";
        if (checkedId == R.id.rb_monika) return "Monika";
        if (checkedId == R.id.rb_natsuki) return "Natsuki";
        if (checkedId == R.id.rb_sayori) return "Sayori";
        if (checkedId == R.id.rb_yuri) return "Yuri";
        return "Konata";
    }

    private int getSelectedSizeDp() {
        int checkedId = rgSize.getCheckedRadioButtonId();
        if (checkedId == R.id.rb_size_small) return 96;
        if (checkedId == R.id.rb_size_large) return 160;
        return 128;
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
                Toast.makeText(this, "Permiso ya concedido", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void updatePermissionUI() {
        boolean granted = checkOverlayPermission();
        if (granted) {
            tvPermissionStatus.setText("CONCEDIDO");
            tvPermissionStatus.setTextColor(getResources().getColor(R.color.success_color));
            tvPermissionStatus.setBackgroundResource(R.drawable.badge_status_ok);
            btnGrantPermission.setEnabled(false);
            btnGrantPermission.setText("PERMISO CONCEDIDO [OK]");
            btnGrantPermission.setAlpha(0.6f);
        } else {
            tvPermissionStatus.setText("PENDIENTE");
            tvPermissionStatus.setTextColor(getResources().getColor(R.color.error_color));
            tvPermissionStatus.setBackgroundResource(R.drawable.badge_status_warn);
            btnGrantPermission.setEnabled(true);
            btnGrantPermission.setText("CONCEDER PERMISO DE SUPERPOSICION");
            btnGrantPermission.setAlpha(1.0f);
        }
    }

    private void startShimeji() {
        if (!checkOverlayPermission()) {
            Toast.makeText(this, "Primero concede el permiso de superposicion", Toast.LENGTH_LONG).show();
            requestOverlayPermission();
            return;
        }

        Intent intent = new Intent(this, ShimejiService.class);
        intent.setAction(ShimejiService.ACTION_START);
        intent.putExtra(ShimejiService.EXTRA_SKIN, getSelectedSkin());
        intent.putExtra(ShimejiService.EXTRA_SIZE_DP, getSelectedSizeDp());
        intent.putExtra(ShimejiService.EXTRA_ZERO_GRAVITY, cbZeroGravity.isChecked());

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent);
        } else {
            startService(intent);
        }

        Toast.makeText(this, "Shimeji activado", Toast.LENGTH_SHORT).show();
    }

    private void stopShimeji() {
        Intent intent = new Intent(this, ShimejiService.class);
        stopService(intent);
        Toast.makeText(this, "Shimeji detenido", Toast.LENGTH_SHORT).show();
    }

    @Override
    protected void onResume() {
        super.onResume();
        updatePermissionUI();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_OVERLAY_PERMISSION) {
            updatePermissionUI();
            if (checkOverlayPermission()) {
                Toast.makeText(this, "Permiso concedido. Ya puedes iniciar el Shimeji", Toast.LENGTH_SHORT).show();
            }
        }
    }
}
