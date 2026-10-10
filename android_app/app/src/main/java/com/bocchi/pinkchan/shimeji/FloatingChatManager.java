package com.bocchi.pinkchan.shimeji;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.HorizontalScrollView;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public class FloatingChatManager {

    private final ShimejiService service;
    private View chatOverlayView;
    private WindowManager.LayoutParams chatParams;
    private boolean isVisible = false;

    private LinearLayout layoutMessages;
    private ScrollView svMessages;
    private EditText etInput;
    private TextView tvHeaderTitle;
    private TextView tvEngineBadge;
    private ImageView ivAvatar;

    private FrameLayout contentContainer;
    private LinearLayout tabChatView;
    private ScrollView tabDialoguesView;
    private ScrollView tabActionsView;

    private TextView btnTabChat;
    private TextView btnTabDialogues;
    private TextView btnTabActions;

    private float initialTouchX, initialTouchY;
    private int initialParamX, initialParamY;
    private GradientDrawable cardBg;
    private LinearLayout mainCard;

    public void applyTheme() {
        if (cardBg == null) return;
        SharedPreferences sp = service.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        int alphaPercent = sp.getInt(MainActivity.KEY_BUBBLE_ALPHA, 92);
        boolean showBorder = sp.getBoolean(MainActivity.KEY_BUBBLE_BORDER, true);
        int alpha255 = (int) (Math.max(20, Math.min(100, alphaPercent)) * 2.55f);
        cardBg.setColor(Color.argb(alpha255, 24, 18, 43));
        if (showBorder) {
            String accentHex = sp.getString("accent_color_hex", "#A382FF");
            int accentColor;
            try {
                accentColor = Color.parseColor(accentHex);
            } catch (Exception e) {
                accentColor = Color.parseColor("#A382FF");
            }
            cardBg.setStroke(service.dpToPx(1.5f), accentColor);
        } else {
            cardBg.setStroke(0, 0);
        }
        if (mainCard != null) {
            mainCard.setBackground(cardBg);
        }
    }

    public FloatingChatManager(ShimejiService service) {
        this.service = service;
        createChatView();
    }

    private void createChatView() {
        int screenWidth = service.getScreenWidth();
        int screenHeight = service.getScreenHeight();

        int cardWidth = Math.min(service.dpToPx(350), screenWidth - service.dpToPx(24));
        int cardHeight = Math.min(service.dpToPx(460), screenHeight - service.dpToPx(60));

        int layoutType;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            layoutType = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        } else {
            layoutType = WindowManager.LayoutParams.TYPE_PHONE;
        }

        chatParams = new WindowManager.LayoutParams(
            cardWidth,
            cardHeight,
            layoutType,
            WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL | WindowManager.LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH,
            PixelFormat.TRANSLUCENT
        );

        chatParams.gravity = Gravity.TOP | Gravity.START;
        chatParams.x = (screenWidth - cardWidth) / 2;
        chatParams.y = service.dpToPx(70);

        // Tarjeta principal flotante
        LinearLayout card = new LinearLayout(service);
        mainCard = card;
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(service.dpToPx(12), service.dpToPx(10), service.dpToPx(12), service.dpToPx(12));

        cardBg = new GradientDrawable();
        cardBg.setShape(GradientDrawable.RECTANGLE);
        cardBg.setCornerRadius(service.dpToPx(16));
        applyTheme();
        card.setBackground(cardBg);
        card.setElevation(service.dpToPx(16));

        // 1. Barra superior de arrastre (Draggable Header)
        LinearLayout headerBar = new LinearLayout(service);
        headerBar.setOrientation(LinearLayout.HORIZONTAL);
        headerBar.setGravity(Gravity.CENTER_VERTICAL);
        headerBar.setPadding(0, 0, 0, service.dpToPx(8));

        ivAvatar = new ImageView(service);
        LinearLayout.LayoutParams ivParams = new LinearLayout.LayoutParams(service.dpToPx(32), service.dpToPx(32));
        ivParams.rightMargin = service.dpToPx(8);
        ivAvatar.setLayoutParams(ivParams);
        headerBar.addView(ivAvatar);

        LinearLayout titleCol = new LinearLayout(service);
        titleCol.setOrientation(LinearLayout.VERTICAL);
        LinearLayout.LayoutParams colParams = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        titleCol.setLayoutParams(colParams);

        tvHeaderTitle = new TextView(service);
        tvHeaderTitle.setText("Chat con Shimeji");
        tvHeaderTitle.setTextColor(Color.parseColor("#F5F3FF"));
        tvHeaderTitle.setTextSize(13);
        tvHeaderTitle.setTypeface(null, Typeface.BOLD);
        titleCol.addView(tvHeaderTitle);

        tvEngineBadge = new TextView(service);
        tvEngineBadge.setText("Motor: Gemini 2.5 Flash / IA");
        tvEngineBadge.setTextColor(Color.parseColor("#C4B5FD"));
        tvEngineBadge.setTextSize(10);
        titleCol.addView(tvEngineBadge);

        headerBar.addView(titleCol);

        // Botón abrir app principal
        TextView btnOpenApp = new TextView(service);
        btnOpenApp.setText("App");
        btnOpenApp.setTextColor(Color.parseColor("#A382FF"));
        btnOpenApp.setTextSize(11);
        btnOpenApp.setPadding(service.dpToPx(8), service.dpToPx(4), service.dpToPx(8), service.dpToPx(4));
        btnOpenApp.setBackgroundResource(R.drawable.chip_action_bg);
        LinearLayout.LayoutParams btnAppParams = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        btnAppParams.rightMargin = service.dpToPx(6);
        btnOpenApp.setLayoutParams(btnAppParams);
        btnOpenApp.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent i = new Intent(service, MainActivity.class);
                i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                service.startActivity(i);
            }
        });
        headerBar.addView(btnOpenApp);

        // Botón cerrar
        TextView btnClose = new TextView(service);
        btnClose.setText("✕");
        btnClose.setTextColor(Color.parseColor("#EF4444"));
        btnClose.setTextSize(14);
        btnClose.setTypeface(null, Typeface.BOLD);
        btnClose.setPadding(service.dpToPx(8), service.dpToPx(4), service.dpToPx(8), service.dpToPx(4));
        btnClose.setBackgroundResource(R.drawable.chip_action_bg);
        btnClose.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                hide();
            }
        });
        headerBar.addView(btnClose);

        // Drag listener en el encabezado
        headerBar.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                boolean isLocked = service.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE)
                    .getBoolean("chat_pos_locked", false);
                if (isLocked) {
                    return false;
                }
                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        initialTouchX = event.getRawX();
                        initialTouchY = event.getRawY();
                        initialParamX = chatParams.x;
                        initialParamY = chatParams.y;
                        return true;
                    case MotionEvent.ACTION_MOVE:
                        chatParams.x = initialParamX + (int) (event.getRawX() - initialTouchX);
                        chatParams.y = initialParamY + (int) (event.getRawY() - initialTouchY);
                        service.getWindowManager().updateViewLayout(chatOverlayView, chatParams);
                        return true;
                    case MotionEvent.ACTION_UP:
                        service.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE)
                            .edit()
                            .putInt("chat_last_x", chatParams.x)
                            .putInt("chat_last_y", chatParams.y)
                            .apply();
                        return true;
                }
                return false;
            }
        });

        card.addView(headerBar);

        // 2. Fila de Pestañas (Tabs: IA, Diálogos, Acciones)
        LinearLayout tabsRow = new LinearLayout(service);
        tabsRow.setOrientation(LinearLayout.HORIZONTAL);
        tabsRow.setPadding(0, 0, 0, service.dpToPx(8));

        btnTabChat = createTabButton("Chat IA", true);
        btnTabDialogues = createTabButton("Diálogos", false);
        btnTabActions = createTabButton("Acciones", false);

        btnTabChat.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectTab(0);
            }
        });
        btnTabDialogues.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectTab(1);
            }
        });
        btnTabActions.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                selectTab(2);
            }
        });

        tabsRow.addView(btnTabChat);
        tabsRow.addView(btnTabDialogues);
        tabsRow.addView(btnTabActions);
        card.addView(tabsRow);

        // 3. Contenedor de contenido de pestañas
        contentContainer = new FrameLayout(service);
        LinearLayout.LayoutParams containerParams = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.0f
        );
        contentContainer.setLayoutParams(containerParams);

        // --- Pestaña 1: Chat con IA ---
        tabChatView = new LinearLayout(service);
        tabChatView.setOrientation(LinearLayout.VERTICAL);

        svMessages = new ScrollView(service);
        LinearLayout.LayoutParams svMsgParams = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.0f
        );
        svMessages.setLayoutParams(svMsgParams);

        layoutMessages = new LinearLayout(service);
        layoutMessages.setOrientation(LinearLayout.VERTICAL);
        layoutMessages.setPadding(0, 0, 0, service.dpToPx(6));
        svMessages.addView(layoutMessages);
        tabChatView.addView(svMessages);

        // Barra inferior de envío
        LinearLayout inputBar = new LinearLayout(service);
        inputBar.setOrientation(LinearLayout.HORIZONTAL);
        inputBar.setGravity(Gravity.CENTER_VERTICAL);
        inputBar.setPadding(0, service.dpToPx(6), 0, 0);

        etInput = new EditText(service);
        etInput.setHint("Escribe un mensaje...");
        etInput.setHintTextColor(Color.parseColor("#94A3B8"));
        etInput.setTextColor(Color.WHITE);
        etInput.setTextSize(12);
        etInput.setBackgroundResource(R.drawable.edittext_bg);
        etInput.setPadding(service.dpToPx(10), service.dpToPx(8), service.dpToPx(10), service.dpToPx(8));
        LinearLayout.LayoutParams etParams = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        etParams.rightMargin = service.dpToPx(6);
        etInput.setLayoutParams(etParams);
        inputBar.addView(etInput);

        TextView btnSend = new TextView(service);
        btnSend.setText("➤ Enviar");
        btnSend.setTextColor(Color.WHITE);
        btnSend.setTextSize(12);
        btnSend.setTypeface(null, Typeface.BOLD);
        btnSend.setBackgroundResource(R.drawable.btn_accent);
        btnSend.setPadding(service.dpToPx(12), service.dpToPx(8), service.dpToPx(12), service.dpToPx(8));
        btnSend.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                sendMessage();
            }
        });
        inputBar.addView(btnSend);

        tabChatView.addView(inputBar);
        contentContainer.addView(tabChatView);

        // --- Pestaña 2: Diálogos prefabricados del personaje ---
        tabDialoguesView = new ScrollView(service);
        tabDialoguesView.setVisibility(View.GONE);
        contentContainer.addView(tabDialoguesView);

        // --- Pestaña 3: Acciones especiales y Salud ---
        tabActionsView = new ScrollView(service);
        tabActionsView.setVisibility(View.GONE);
        contentContainer.addView(tabActionsView);

        card.addView(contentContainer);
        chatOverlayView = card;
    }

    private TextView createTabButton(String title, boolean selected) {
        TextView tv = new TextView(service);
        tv.setText(title);
        tv.setTextSize(11);
        tv.setTypeface(null, Typeface.BOLD);
        tv.setPadding(service.dpToPx(10), service.dpToPx(6), service.dpToPx(10), service.dpToPx(6));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        lp.rightMargin = service.dpToPx(4);
        tv.setLayoutParams(lp);
        tv.setGravity(Gravity.CENTER);
        applyTabStyle(tv, selected);
        return tv;
    }

    private void applyTabStyle(TextView tv, boolean selected) {
        GradientDrawable gd = new GradientDrawable();
        gd.setShape(GradientDrawable.RECTANGLE);
        gd.setCornerRadius(service.dpToPx(8));
        if (selected) {
            gd.setColor(Color.parseColor("#7C3AED"));
            tv.setTextColor(Color.WHITE);
        } else {
            gd.setColor(Color.parseColor("#251E3E"));
            tv.setTextColor(Color.parseColor("#C4B5FD"));
        }
        tv.setBackground(gd);
    }

    private void selectTab(int index) {
        applyTabStyle(btnTabChat, index == 0);
        applyTabStyle(btnTabDialogues, index == 1);
        applyTabStyle(btnTabActions, index == 2);

        tabChatView.setVisibility(index == 0 ? View.VISIBLE : View.GONE);
        tabDialoguesView.setVisibility(index == 1 ? View.VISIBLE : View.GONE);
        tabActionsView.setVisibility(index == 2 ? View.VISIBLE : View.GONE);

        if (index == 1) {
            populateDialoguesTab();
        } else if (index == 2) {
            populateActionsTab();
        }
    }

    private void populateDialoguesTab() {
        ShimejiEntity entity = service.getPrimaryShimeji();
        if (entity == null) return;

        LinearLayout layout = new LinearLayout(service);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(0, 0, 0, service.dpToPx(10));

        TextView tvHeader = new TextView(service);
        tvHeader.setText("Toca una frase para que " + entity.skin.name + " la diga en pantalla:");
        tvHeader.setTextColor(Color.parseColor("#A382FF"));
        tvHeader.setTextSize(11);
        tvHeader.setPadding(0, 0, 0, service.dpToPx(8));
        layout.addView(tvHeader);

        String[] dl = entity.skin.dialogues;
        for (final String line : dl) {
            TextView btnLine = new TextView(service);
            btnLine.setText("• " + line);
            btnLine.setTextColor(Color.parseColor("#E0D8FF"));
            btnLine.setTextSize(11);
            btnLine.setBackgroundResource(R.drawable.chip_action_bg);
            btnLine.setPadding(service.dpToPx(8), service.dpToPx(6), service.dpToPx(8), service.dpToPx(6));
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
            );
            lp.bottomMargin = service.dpToPx(5);
            btnLine.setLayoutParams(lp);

            btnLine.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    ShimejiEntity e = service.getPrimaryShimeji();
                    if (e != null) {
                        e.say(line, 3000);
                        service.triggerHaptic(25);
                    }
                }
            });
            layout.addView(btnLine);
        }

        tabDialoguesView.removeAllViews();
        tabDialoguesView.addView(layout);
    }

    private void populateActionsTab() {
        final ShimejiEntity entity = service.getPrimaryShimeji();
        if (entity == null) return;

        LinearLayout layout = new LinearLayout(service);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(0, 0, 0, service.dpToPx(10));

        // Estado de Salud (HP)
        TextView tvHp = new TextView(service);
        tvHp.setText("Salud de " + entity.skin.name + ": " + entity.hp + "/100 HP" + (entity.isKo ? " (¡K.O.!)" : ""));
        tvHp.setTextColor(entity.hp > 30 ? Color.parseColor("#34D399") : Color.parseColor("#F87171"));
        tvHp.setTextSize(12);
        tvHp.setTypeface(null, Typeface.BOLD);
        tvHp.setPadding(0, 0, 0, service.dpToPx(8));
        layout.addView(tvHp);

        // Fila: Curar y Lanzar
        LinearLayout rowHealth = new LinearLayout(service);
        rowHealth.setOrientation(LinearLayout.HORIZONTAL);
        rowHealth.setPadding(0, 0, 0, service.dpToPx(8));

        TextView btnHeal = new TextView(service);
        btnHeal.setText("Curar y Alimentar (100 HP)");
        btnHeal.setTextColor(Color.WHITE);
        btnHeal.setTextSize(11);
        btnHeal.setTypeface(null, Typeface.BOLD);
        btnHeal.setBackgroundResource(R.drawable.btn_accent);
        btnHeal.setPadding(service.dpToPx(10), service.dpToPx(6), service.dpToPx(10), service.dpToPx(6));
        LinearLayout.LayoutParams lpHeal = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        lpHeal.rightMargin = service.dpToPx(4);
        btnHeal.setLayoutParams(lpHeal);
        btnHeal.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                entity.heal(100, "pastelito y té");
                populateActionsTab();
            }
        });
        rowHealth.addView(btnHeal);

        TextView btnFling = new TextView(service);
        btnFling.setText("Lanzar (Fling)");
        btnFling.setTextColor(Color.WHITE);
        btnFling.setTextSize(11);
        btnFling.setTypeface(null, Typeface.BOLD);
        btnFling.setBackgroundResource(R.drawable.chip_action_bg);
        btnFling.setPadding(service.dpToPx(10), service.dpToPx(6), service.dpToPx(10), service.dpToPx(6));
        btnFling.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT));
        btnFling.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                entity.flingUpwards();
            }
        });
        rowHealth.addView(btnFling);
        layout.addView(rowHealth);

        // Acciones especiales de la skin
        TextView tvSpecial = new TextView(service);
        tvSpecial.setText("Acciones personalizadas de " + entity.skin.name + ":");
        tvSpecial.setTextColor(Color.parseColor("#A382FF"));
        tvSpecial.setTextSize(11);
        tvSpecial.setTypeface(null, Typeface.BOLD);
        tvSpecial.setPadding(0, service.dpToPx(4), 0, service.dpToPx(6));
        layout.addView(tvSpecial);

        String[][] customActs = SkinData.getCustomActions(entity.skin.id);
        for (int i = 0; i < customActs.length; i++) {
            final int actIdx = i;
            String label = customActs[i][0];
            String speech = customActs[i][4];

            TextView btnAct = new TextView(service);
            btnAct.setText(label + " -> \"" + speech + "\"");
            btnAct.setTextColor(Color.parseColor("#F5F3FF"));
            btnAct.setTextSize(11);
            btnAct.setBackgroundResource(R.drawable.chip_action_bg);
            btnAct.setPadding(service.dpToPx(8), service.dpToPx(6), service.dpToPx(8), service.dpToPx(6));
            LinearLayout.LayoutParams lpAct = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
            );
            lpAct.bottomMargin = service.dpToPx(5);
            btnAct.setLayoutParams(lpAct);

            btnAct.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    entity.triggerCustomAction(actIdx);
                }
            });
            layout.addView(btnAct);
        }

        // Acciones generales del sistema
        TextView tvSys = new TextView(service);
        tvSys.setText("Herramientas útiles del sistema:");
        tvSys.setTextColor(Color.parseColor("#A382FF"));
        tvSys.setTextSize(11);
        tvSys.setTypeface(null, Typeface.BOLD);
        tvSys.setPadding(0, service.dpToPx(6), 0, service.dpToPx(6));
        layout.addView(tvSys);

        LinearLayout rowSys = new LinearLayout(service);
        rowSys.setOrientation(LinearLayout.HORIZONTAL);

        TextView btnTermux = createActionButton("Termux", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                service.openTermux();
            }
        });
        TextView btnFiles = createActionButton("Archivos", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                service.createFilesAndFolder();
            }
        });
        TextView btnItem = createActionButton("Soltar Snack", new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                service.dropRandomItem();
            }
        });

        rowSys.addView(btnTermux);
        rowSys.addView(btnFiles);
        rowSys.addView(btnItem);
        layout.addView(rowSys);

        tabActionsView.removeAllViews();
        tabActionsView.addView(layout);
    }

    private TextView createActionButton(String label, View.OnClickListener listener) {
        TextView tv = new TextView(service);
        tv.setText(label);
        tv.setTextColor(Color.parseColor("#C4B5FD"));
        tv.setTextSize(11);
        tv.setBackgroundResource(R.drawable.chip_action_bg);
        tv.setPadding(service.dpToPx(8), service.dpToPx(6), service.dpToPx(8), service.dpToPx(6));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        lp.rightMargin = service.dpToPx(4);
        tv.setLayoutParams(lp);
        tv.setGravity(Gravity.CENTER);
        tv.setOnClickListener(listener);
        return tv;
    }

    private void sendMessage() {
        if (etInput == null) return;
        final String text = etInput.getText().toString().trim();
        if (text.isEmpty()) return;
        etInput.setText("");

        final ShimejiEntity entity = service.getPrimaryShimeji();
        final String skinId = (entity != null) ? entity.skin.id : "Monika";
        final String skinName = (entity != null) ? entity.skin.name : "Monika";

        addBubble("Tú", text, true);

        // Indicador de escritura
        final TextView tvThinking = addBubble(skinName, skinName + " está pensando...", false);

        AiEngineHelper.askAi(service, skinId, text, new AiEngineHelper.AiCallback() {
            @Override
            public void onSuccess(final String reply) {
                if (layoutMessages != null) {
                    layoutMessages.removeView(tvThinking);
                    addBubble(skinName, reply, false);
                }
                if (entity != null) {
                    int bubbleDur = Math.max(5000, Math.min(35000, reply.length() * 85));
                    entity.say(reply, bubbleDur);
                    service.triggerHaptic(20);
                }
                if (service != null) {
                    service.speakTts(reply);
                }
            }

            @Override
            public void onError(final String errorMsg) {
                if (layoutMessages != null) {
                    layoutMessages.removeView(tvThinking);
                    addBubble(skinName, "[!] " + errorMsg, false);
                }
            }
        });
    }

    public TextView addSystemMessage(final String message) {
        if (service != null && service.getHandler() != null) {
            service.getHandler().post(new Runnable() {
                @Override
                public void run() {
                    addBubble("JARVIS", message, false);
                }
            });
        }
        return null;
    }

    private TextView addBubble(String sender, String message, boolean isUser) {
        TextView bubble = new TextView(service);
        bubble.setText(sender + ":\n" + message);
        bubble.setTextSize(11);
        bubble.setPadding(service.dpToPx(10), service.dpToPx(6), service.dpToPx(10), service.dpToPx(6));

        GradientDrawable bg = new GradientDrawable();
        bg.setShape(GradientDrawable.RECTANGLE);
        bg.setCornerRadius(service.dpToPx(10));
        if (isUser) {
            bg.setColor(Color.parseColor("#4C1D95")); // Violeta usuario
            bubble.setTextColor(Color.WHITE);
        } else {
            bg.setColor(Color.parseColor("#1F1934")); // Fondo mensaje personaje
            bubble.setTextColor(Color.parseColor("#EDE9FE"));
            SharedPreferences sp = service.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
            String accentHex = sp.getString("accent_color_hex", "#7C3AED");
            int accentColor;
            try {
                accentColor = Color.parseColor(accentHex);
            } catch (Exception e) {
                accentColor = Color.parseColor("#7C3AED");
            }
            bg.setStroke(service.dpToPx(1), accentColor);
        }
        bubble.setBackground(bg);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT
        );
        lp.bottomMargin = service.dpToPx(6);
        bubble.setLayoutParams(lp);

        layoutMessages.addView(bubble);
        svMessages.post(new Runnable() {
            @Override
            public void run() {
                svMessages.fullScroll(View.FOCUS_DOWN);
            }
        });
        return bubble;
    }

    public void show() {
        ShimejiEntity entity = service.getPrimaryShimeji();
        if (entity != null) {
            tvHeaderTitle.setText("Chat con " + entity.skin.name);
            SharedPreferences sp = service.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
            String aiMode = sp.getString(MainActivity.KEY_AI_MODE, "local");
            if ("gemini".equalsIgnoreCase(aiMode)) {
                String mName = sp.getString(MainActivity.KEY_GEMINI_MODEL, "gemini-2.5-flash");
                tvEngineBadge.setText("Motor: Gemini (" + mName + ")");
            } else if ("cloud".equalsIgnoreCase(aiMode)) {
                tvEngineBadge.setText("Motor: Custom Cloud / Ollama");
            } else {
                tvEngineBadge.setText("Motor: Local Offline");
            }
        }

        if (!isVisible) {
            try {
                service.getWindowManager().addView(chatOverlayView, chatParams);
                isVisible = true;
            } catch (Exception ignored) {}
        } else {
            chatOverlayView.setVisibility(View.VISIBLE);
        }
    }

    public void hide() {
        if (isVisible && chatOverlayView != null) {
            chatOverlayView.setVisibility(View.GONE);
        }
    }

    public void destroy() {
        if (isVisible && chatOverlayView != null) {
            try {
                service.getWindowManager().removeView(chatOverlayView);
            } catch (Exception ignored) {}
            isVisible = false;
        }
    }
}

