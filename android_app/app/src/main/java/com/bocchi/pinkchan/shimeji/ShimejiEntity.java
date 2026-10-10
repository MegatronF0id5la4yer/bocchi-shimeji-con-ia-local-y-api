package com.bocchi.pinkchan.shimeji;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.PixelFormat;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.io.File;
import java.util.Random;

public class ShimejiEntity {

    public final int id;
    private final ShimejiService service;
    public SkinData skin;

    public View overlayView;
    public ImageView ivSprite;
    public TextView tvSpeechBubble;
    public LinearLayout layoutLongPressMenu;
    public WindowManager.LayoutParams params;

    public float posX, posY;
    public float velX, velY;
    public float currentFloorY;
    public int facing = 1;
    public String state = "STAND";
    public int stateTimer = 90;
    public int tickCount = 0;
    public boolean zeroGravity = false;

    public int hp = 100;
    public boolean isKo = false;
    public int koTimer = 0;
    public int cprCount = 0;
    public int shakeTicks = 0;
    public String customFrameName1 = null;
    public String customFrameName2 = null;
    public String customActionDialogue = null;

    private boolean isDragging = false;
    private float touchStartX, touchStartY;
    private float initialPosX, initialPosY;
    private long touchStartTime;
    private float lastMoveX, lastMoveY;
    private long lastMoveTime;
    private boolean isLongPressTriggered = false;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private Runnable hideBubbleRunnable;
    private Runnable longPressRunnable;
    private final Random random = new Random();

    public ShimejiEntity(ShimejiService service, int id, SkinData skin, float startX, float startY) {
        this.service = service;
        this.id = id;
        this.skin = skin;
        this.posX = startX;
        this.posY = startY;
        this.currentFloorY = startY;

        setupView();
    }

    private void setupView() {
        LayoutInflater inflater = LayoutInflater.from(service);
        overlayView = inflater.inflate(R.layout.view_shimeji_overlay, null);

        ivSprite = overlayView.findViewById(R.id.shimeji_image_view);
        tvSpeechBubble = overlayView.findViewById(R.id.shimeji_speech_bubble);
        layoutLongPressMenu = overlayView.findViewById(R.id.shimeji_longpress_menu);

        int sizePx = service.getSizePx();
        ivSprite.getLayoutParams().width = sizePx;
        ivSprite.getLayoutParams().height = sizePx;

        int layoutType;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            layoutType = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        } else {
            layoutType = WindowManager.LayoutParams.TYPE_PHONE;
        }

        params = new WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        );

        params.gravity = Gravity.TOP | Gravity.START;
        params.x = (int) posX;
        params.y = (int) posY;

        setupMenuListeners();
        setupTouchEvents();

        service.getWindowManager().addView(overlayView, params);
        updateSprite();
        say("Holi, aqui estoy.", 2400);
    }

    private void setupMenuListeners() {
        // Asistente de Voz
        overlayView.findViewById(R.id.btn_menu_voice).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                hideMenu();
                service.startVoiceAssistant();
            }
        });

        // Chat Interactivo Flotante Fuera de la App
        View btnChat = overlayView.findViewById(R.id.btn_menu_chat);
        if (btnChat != null) {
            btnChat.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    hideMenu();
                    service.showFloatingChat();
                }
            });
        }

        // Cambiar Skin
        overlayView.findViewById(R.id.btn_menu_skin).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                cycleSkin();
                hideMenu();
            }
        });

        // Acariciar y Curar
        overlayView.findViewById(R.id.btn_menu_pet).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                hideMenu();
                heal(30, "caricias");
            }
        });

        // Invocar Otro Shimeji
        overlayView.findViewById(R.id.btn_menu_clone).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                hideMenu();
                service.spawnExtraShimeji(SkinData.getNextSkin(skin.id));
            }
        });

        // Acciones Dinamicas de la Skin (botones superiores de accion)
        updateCustomActionMenuButtons();

        // Jugar
        View btnPlay = overlayView.findViewById(R.id.btn_menu_play);
        if (btnPlay != null) {
            btnPlay.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    hideMenu();
                    service.triggerAction("play");
                }
            });
        }

        // Bailar
        View btnDance = overlayView.findViewById(R.id.btn_menu_dance);
        if (btnDance != null) {
            btnDance.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    hideMenu();
                    service.triggerAction("dance");
                }
            });
        }

        // Termux
        View btnTermux = overlayView.findViewById(R.id.btn_menu_termux);
        if (btnTermux != null) {
            btnTermux.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    hideMenu();
                    service.openTermux();
                }
            });
        }

        // Archivos
        View btnFiles = overlayView.findViewById(R.id.btn_menu_files);
        if (btnFiles != null) {
            btnFiles.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    hideMenu();
                    service.createFilesAndFolder();
                }
            });
        }

        // Soltar Item
        View btnItem = overlayView.findViewById(R.id.btn_menu_item);
        if (btnItem != null) {
            btnItem.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    hideMenu();
                    service.dropRandomItem();
                }
            });
        }

        // Flotar / Gravedad
        overlayView.findViewById(R.id.btn_menu_gravity).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                zeroGravity = !zeroGravity;
                state = "ROAM";
                velY = -service.dpToPx(3);
                velX = (random.nextBoolean() ? 1 : -1) * service.dpToPx(2);
                say(zeroGravity ? "Flotando por la pantalla." : "Gravedad normal.", 2200);
                hideMenu();
            }
        });

        // Quitar este Shimeji
        overlayView.findViewById(R.id.btn_menu_remove).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                hideMenu();
                service.removeShimeji(ShimejiEntity.this);
            }
        });

        // Cerrar menu
        overlayView.findViewById(R.id.btn_menu_close).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                hideMenu();
            }
        });
    }

    public void updateCustomActionMenuButtons() {
        TextView btnAct1 = overlayView.findViewById(R.id.btn_menu_guitar);
        TextView btnAct2 = overlayView.findViewById(R.id.btn_menu_box);
        String[][] customActs = SkinData.getCustomActions(skin.id);
        if (btnAct1 != null && customActs.length > 0) {
            btnAct1.setText(customActs[0][0]);
            btnAct1.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    hideMenu();
                    triggerCustomAction(0);
                }
            });
        }
        if (btnAct2 != null && customActs.length > 1) {
            btnAct2.setText(customActs[1][0]);
            btnAct2.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    hideMenu();
                    triggerCustomAction(1);
                }
            });
        }
    }

    public void takeDamage(int amount) {
        if (amount <= 0) return;
        hp = Math.max(0, hp - amount);
        shakeTicks = 14;
        service.triggerHaptic(60);

        String[] cries = SkinData.getPainPhrases(skin.id);
        String cry = (cries != null && cries.length > 0) ? cries[random.nextInt(cries.length)] : "OUCH!!";
        say(cry + " (-" + amount + " HP, me quedan " + hp + " HP)", 3200);

        if (hp <= 0 && !isKo) {
            triggerKo();
        }
    }

    public void heal(int amount, String source) {
        if (amount <= 0) return;
        if (isKo) {
            recoverFromKo();
        }
        hp = Math.min(100, hp + amount);
        service.triggerHaptic(25);
        say("+" + amount + " HP (" + source + ")! Ahora tengo " + hp + " HP. <3", 2800);
    }

    public void triggerKo() {
        isKo = true;
        state = "KO";
        koTimer = 220;
        cprCount = 0;
        velY = -service.dpToPx(12f);
        velX = (random.nextBoolean() ? 1 : -1) * service.dpToPx(5f);
        service.triggerHaptic(120);

        service.dropRandomItem();
        logDeathDiary();

        say("[K.O.] Me quede sin vida... Solte botin!\nToca repetidamente para RCP (0/3) o espera a revivir!", 5000);
    }

    public void cprPress() {
        if (!isKo) return;
        cprCount++;
        service.triggerHaptic(45);
        if (cprCount >= 3) {
            cprRevive();
        } else {
            say("[RCP] (" + cprCount + "/3) *bombeando pecho*\nSigue tocando rapido!", 1800);
        }
    }

    public void cprRevive() {
        isKo = false;
        koTimer = 0;
        cprCount = 0;
        hp = 75;
        state = "STAND";
        stateTimer = 60;
        service.triggerHaptic(85);
        say("DESFIBRILADOR EXITOSO! (+75 HP) [★]\nGracias por salvarme la vida!", 3200);
    }

    private void logDeathDiary() {
        try {
            File jdir = new File(service.getFilesDir(), "JarvisFiles");
            if (!jdir.exists()) jdir.mkdirs();
            File dpath = new File(jdir, "diario_de_defuncion.txt");
            java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.getDefault());
            String nowStr = sdf.format(new java.util.Date());
            String[] quotes = new String[]{
                "Fue un honor acompanarte en Android... alimenta al proximo Shimeji.",
                "Los toques y las caidas fueron implacables hoy...",
                "Vi pasar todos mis frames ante mis ojos...",
                "Dile a Monika que guarde un respaldo de mis recuerdos...",
                "Volvere pronto, o cuando me des RCP..."
            };
            String quote = quotes[random.nextInt(quotes.length)];
            String entry = "[" + nowStr + "] DEFUNCION DE " + skin.name.toUpperCase() + "\n" +
                "Causa: Agotamiento total de HP por impacto o caida.\n" +
                "Ultimas palabras: \"" + quote + "\"\n" +
                "Estado: Botin arrojado. Reanimacion RCP disponible.\n" +
                "--------------------------------------------------\n";
            java.io.FileOutputStream fos = new java.io.FileOutputStream(dpath, true);
            fos.write(entry.getBytes("UTF-8"));
            fos.close();
        } catch (Exception ignored) {}
    }

    public void recoverFromKo() {
        isKo = false;
        koTimer = 0;
        cprCount = 0;
        hp = Math.max(30, hp);
        state = "STAND";
        stateTimer = 60;
        service.triggerHaptic(35);
        say("Revivi con energias renovadas! Muchas gracias! <3", 2800);
    }

    public void flingUpwards() {
        state = "FLUNG";
        velY = -service.dpToPx(19f);
        velX = (random.nextBoolean() ? 1 : -1) * (service.dpToPx(10f) + random.nextFloat() * service.dpToPx(6f));
        service.triggerHaptic(45);
        say("WAAAAA!! A volar por los aires!", 2400);
    }

    public void triggerCustomAction(int actionIndex) {
        String[][] actions = SkinData.getCustomActions(skin.id);
        if (actions != null && actionIndex >= 0 && actionIndex < actions.length) {
            String[] act = actions[actionIndex];
            state = "CUSTOM_ACTION";
            stateTimer = 110;
            customFrameName1 = act[2];
            customFrameName2 = act[3];
            customActionDialogue = act[4];
            say(act[4], 3200);
            service.triggerHaptic(30);
        }
    }

    public void setSkin(SkinData newSkin) {
        if (newSkin == null) return;
        this.skin = newSkin;
        updateCustomActionMenuButtons();
        updateSprite();
        say("Hola! Soy " + skin.name + "!", 2500);
    }

    public void cycleSkin() {
        String nextId = SkinData.getNextSkin(skin.id);
        SkinData newSkin = SkinData.get(nextId);
        service.triggerHaptic(35);
        setSkin(newSkin);
    }

    public void showMenu() {
        isLongPressTriggered = true;
        service.triggerHaptic(50);
        if (layoutLongPressMenu != null) {
            TextView tvTitle = overlayView.findViewById(R.id.tv_menu_title);
            if (tvTitle != null) {
                tvTitle.setText(skin.name + " (" + hp + " HP)" + (isKo ? " [K.O.]" : ""));
            }
            updateCustomActionMenuButtons();
            layoutLongPressMenu.setVisibility(View.VISIBLE);
            tvSpeechBubble.setVisibility(View.GONE);
            state = "STAND";
            velX = 0;
            velY = 0;
        }
    }

    public void hideMenu() {
        if (layoutLongPressMenu != null) {
            layoutLongPressMenu.setVisibility(View.GONE);
        }
    }

    private void setupTouchEvents() {
        overlayView.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        if (isKo) {
                            cprPress();
                            return true;
                        }
                        isDragging = true;
                        isLongPressTriggered = false;
                        touchStartTime = System.currentTimeMillis();
                        touchStartX = event.getRawX();
                        touchStartY = event.getRawY();
                        initialPosX = posX;
                        initialPosY = posY;

                        lastMoveX = touchStartX;
                        lastMoveY = touchStartY;
                        lastMoveTime = touchStartTime;

                        state = "FALL";
                        velX = 0;
                        velY = 0;
                        updateSprite();

                        longPressRunnable = new Runnable() {
                            @Override
                            public void run() {
                                if (isDragging && !isLongPressTriggered) {
                                    showMenu();
                                }
                            }
                        };
                        handler.postDelayed(longPressRunnable, 420);
                        return true;

                    case MotionEvent.ACTION_MOVE:
                        if (!isDragging) return false;
                        float curX = event.getRawX();
                        float curY = event.getRawY();

                        float dist = (float) Math.hypot(curX - touchStartX, curY - touchStartY);
                        if (dist > service.dpToPx(10)) {
                            handler.removeCallbacks(longPressRunnable);
                            if (layoutLongPressMenu.getVisibility() == View.VISIBLE) {
                                hideMenu();
                            }
                        }

                        int szMove = service.getSizePx();
                        int screenWMove = service.getScreenWidth();
                        int screenHMove = service.getScreenHeight();
                        int topMarginMove = service.dpToPx(24);
                        int bottomMarginMove = screenHMove - szMove - service.dpToPx(35);

                        // Clamp estrictamente a los bordes visibles de la pantalla
                        posX = Math.max(0, Math.min(screenWMove - szMove, initialPosX + (curX - touchStartX)));
                        posY = Math.max(topMarginMove, Math.min(bottomMarginMove, initialPosY + (curY - touchStartY)));

                        params.x = (int) posX;
                        params.y = (int) posY;
                        service.getWindowManager().updateViewLayout(overlayView, params);

                        lastMoveX = curX;
                        lastMoveY = curY;
                        lastMoveTime = System.currentTimeMillis();
                        return true;

                    case MotionEvent.ACTION_UP:
                        if (!isDragging) return false;
                        isDragging = false;
                        handler.removeCallbacks(longPressRunnable);

                        int szUp = service.getSizePx();
                        int screenWUp = service.getScreenWidth();
                        int screenHUp = service.getScreenHeight();
                        int topMarginUp = service.dpToPx(24);
                        int bottomMarginUp = screenHUp - szUp - service.dpToPx(35);

                        posX = Math.max(0, Math.min(screenWUp - szUp, posX));
                        posY = Math.max(topMarginUp, Math.min(bottomMarginUp, posY));

                        if (isLongPressTriggered) return true;

                        float totalDist = (float) Math.hypot(event.getRawX() - touchStartX, event.getRawY() - touchStartY);
                        long duration = System.currentTimeMillis() - touchStartTime;

                        // Caricia suave prolongada (>500ms y sin moverse mucho) -> Cura HP!
                        if (totalDist < service.dpToPx(16) && duration >= 500) {
                            heal(20, "caricias");
                            return true;
                        }

                        if (totalDist < service.dpToPx(12) && duration < 380) {
                            onPoke();
                        } else {
                            currentFloorY = Math.min(bottomMarginUp, Math.max(topMarginUp, posY));

                            long dt = System.currentTimeMillis() - lastMoveTime;
                            if (dt > 0 && dt < 160) {
                                float flingVx = (event.getRawX() - lastMoveX) * 1.25f;
                                float flingVy = (event.getRawY() - lastMoveY) * 1.25f;
                                float maxSpd = service.dpToPx(30f);
                                velX = Math.max(-maxSpd, Math.min(maxSpd, flingVx));
                                velY = Math.max(-maxSpd, Math.min(maxSpd, flingVy));

                                if (Math.hypot(velX, velY) > service.dpToPx(8f)) {
                                    state = "FLUNG";
                                    service.triggerHaptic(30);
                                } else {
                                    state = zeroGravity ? "ROAM" : "FALL";
                                    service.triggerHaptic(15);
                                }
                            } else {
                                velX = 0;
                                velY = zeroGravity ? 0 : 2f;
                                state = zeroGravity ? "ROAM" : "FALL";
                                service.triggerHaptic(15);
                            }
                        }
                        return true;
                }
                return false;
            }
        });
    }

    private void onPoke() {
        service.triggerHaptic(35);
        state = "STAND";
        stateTimer = 50;

        String[] poked = skin.poked;
        if (poked.length > 0) {
            say(poked[random.nextInt(poked.length)], 2500);
        }
    }

    public void applyBubbleStyle() {
        if (tvSpeechBubble == null) return;
        android.content.SharedPreferences sp = service.getSharedPreferences(MainActivity.PREFS_NAME, android.content.Context.MODE_PRIVATE);
        int alphaPercent = sp.getInt(MainActivity.KEY_BUBBLE_ALPHA, 90);
        boolean showBorder = sp.getBoolean(MainActivity.KEY_BUBBLE_BORDER, true);

        int alpha = (int) (Math.max(10, Math.min(100, alphaPercent)) * 2.55f);
        android.graphics.drawable.GradientDrawable gd = new android.graphics.drawable.GradientDrawable();
        gd.setShape(android.graphics.drawable.GradientDrawable.RECTANGLE);
        gd.setCornerRadius(service.dpToPx(14));
        gd.setColor(android.graphics.Color.argb(alpha, 0x1A, 0x14, 0x2A));
        if (showBorder) {
            int strokeColor = android.graphics.Color.argb(Math.min(255, alpha + 50), 0x8A, 0x56, 0xE2);
            gd.setStroke(service.dpToPx(1.5f), strokeColor);
        } else {
            gd.setStroke(0, 0);
        }
        tvSpeechBubble.setBackground(gd);
    }

    public void say(String text, int durationMs) {
        if (tvSpeechBubble == null) return;
        applyBubbleStyle();
        tvSpeechBubble.setText(text);
        tvSpeechBubble.setVisibility(View.VISIBLE);

        if (hideBubbleRunnable != null) {
            handler.removeCallbacks(hideBubbleRunnable);
        }
        hideBubbleRunnable = new Runnable() {
            @Override
            public void run() {
                if (tvSpeechBubble != null) {
                    tvSpeechBubble.setVisibility(View.GONE);
                }
            }
        };
        int effectiveDuration = Math.max(durationMs, Math.min(35000, (text != null ? text.length() : 0) * 85));
        handler.postDelayed(hideBubbleRunnable, effectiveDuration);
    }

    public void updatePhysics(int screenWidth, int screenHeight, boolean globalZeroGravity) {
        if (isDragging || overlayView == null) return;

        if ("KO".equals(state) || isKo) {
            velX = 0;
            velY = 0;
            koTimer--;
            if (koTimer <= 0) {
                recoverFromKo();
            }
            updateSprite();
            params.x = (int) posX;
            params.y = (int) posY;
            service.getWindowManager().updateViewLayout(overlayView, params);
            return;
        }

        boolean isZeroG = zeroGravity || globalZeroGravity;
        int sizePx = service.getSizePx();
        int leftEdge = 0;
        int rightEdge = Math.max(0, screenWidth - sizePx);
        int topEdge = service.dpToPx(24);
        int bottomEdge = Math.max(topEdge, screenHeight - sizePx - service.dpToPx(35));

        tickCount++;

        // 1. Caida y Lanzamiento con fisicas elasticas y dano
        if ("FALL".equals(state) || "FLUNG".equals(state)) {
            SharedPreferences sp = service.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
            float gravMult = sp.getFloat("shimeji_gravity_mult", 1.0f);
            boolean allowClimb = sp.getBoolean("allow_wall_climb", true);
            float gravity = (isZeroG ? 0.05f : service.dpToPx(1.35f)) * gravMult;
            velX *= 0.985f;
            velY *= 0.992f;
            velY += gravity;
            posX += velX;
            posY += velY;

            // Rebote pared izquierda
            if (posX <= leftEdge) {
                posX = leftEdge;
                float impactSpeed = Math.abs(velX);
                if (impactSpeed > service.dpToPx(11f)) {
                    takeDamage((int) (impactSpeed / service.dpToPx(2.2f)));
                }
                velX = -velX * 0.70f;
                if (allowClimb && Math.abs(velX) < service.dpToPx(1.5f) && random.nextFloat() < 0.35f) {
                    state = "CLIMB_LEFT";
                    velY = -service.dpToPx(2.2f);
                }
            }
            // Rebote pared derecha
            else if (posX >= rightEdge) {
                posX = rightEdge;
                float impactSpeed = Math.abs(velX);
                if (impactSpeed > service.dpToPx(11f)) {
                    takeDamage((int) (impactSpeed / service.dpToPx(2.2f)));
                }
                velX = -velX * 0.70f;
                if (allowClimb && Math.abs(velX) < service.dpToPx(1.5f) && random.nextFloat() < 0.35f) {
                    state = "CLIMB_RIGHT";
                    velY = -service.dpToPx(2.2f);
                }
            }

            // Rebote techo
            if (posY <= topEdge) {
                posY = topEdge;
                float impactSpeed = Math.abs(velY);
                if (impactSpeed > service.dpToPx(11f)) {
                    takeDamage((int) (impactSpeed / service.dpToPx(2.2f)));
                }
                velY = -velY * 0.70f;
            }
            // Rebote piso
            else if (posY >= currentFloorY) {
                posY = currentFloorY;
                float impactSpeed = Math.abs(velY);
                if (impactSpeed > service.dpToPx(13f)) {
                    takeDamage((int) (impactSpeed / service.dpToPx(2.2f)));
                }
                if (Math.abs(velY) > service.dpToPx(3.5f)) {
                    velY = -velY * 0.58f;
                    velX *= 0.72f;
                    service.triggerHaptic(12);
                } else {
                    velY = 0;
                    velX = 0;
                    state = "STAND";
                    stateTimer = 40 + random.nextInt(60);
                    service.triggerHaptic(10);
                }
            }
        }
        // 2. Caminar horizontalmente en su nivel actual
        else if ("WALK".equals(state)) {
            posX += velX;

            if (posX <= leftEdge) {
                posX = leftEdge;
                float choice = random.nextFloat();
                if (choice < 0.4f) {
                    state = "CLIMB_LEFT";
                    velY = -service.dpToPx(2.2f);
                } else if (choice < 0.7f) {
                    state = "ROAM";
                    velY = (random.nextBoolean() ? 1 : -1) * service.dpToPx(2);
                    velX = service.dpToPx(2);
                } else {
                    facing = 1;
                    velX = Math.abs(velX);
                }
            } else if (posX >= rightEdge) {
                posX = rightEdge;
                float choice = random.nextFloat();
                if (choice < 0.4f) {
                    state = "CLIMB_RIGHT";
                    velY = -service.dpToPx(2.2f);
                } else if (choice < 0.7f) {
                    state = "ROAM";
                    velY = (random.nextBoolean() ? 1 : -1) * service.dpToPx(2);
                    velX = -service.dpToPx(2);
                } else {
                    facing = -1;
                    velX = -Math.abs(velX);
                }
            }

            stateTimer--;
            if (stateTimer <= 0) pickRandomState();
        }
        // 3. Navegacion 2D por toda la pantalla (ROAM)
        else if ("ROAM".equals(state)) {
            posX += velX;
            posY += velY;

            if (posX <= leftEdge) {
                posX = leftEdge;
                velX = Math.abs(velX);
                facing = 1;
            } else if (posX >= rightEdge) {
                posX = rightEdge;
                velX = -Math.abs(velX);
                facing = -1;
            }

            if (posY <= topEdge) {
                posY = topEdge;
                velY = Math.abs(velY);
                if (random.nextFloat() < 0.5f) {
                    state = "CEILING";
                    velX = facing * service.dpToPx(1.8f);
                }
            } else if (posY >= bottomEdge) {
                posY = bottomEdge;
                velY = -Math.abs(velY);
            }

            currentFloorY = posY;
            stateTimer--;
            if (stateTimer <= 0) pickRandomState();
        }
        // 4. Trepar pared izquierda
        else if ("CLIMB_LEFT".equals(state)) {
            posX = leftEdge;
            posY += (velY != 0 ? velY : -service.dpToPx(2.2f));
            facing = 1;

            if (posY <= topEdge) {
                posY = topEdge;
                state = "CEILING";
                facing = 1;
                velX = service.dpToPx(2f);
            } else if (posY >= bottomEdge) {
                posY = bottomEdge;
                state = "WALK";
                velX = service.dpToPx(2f);
            }
        }
        // 5. Trepar pared derecha
        else if ("CLIMB_RIGHT".equals(state)) {
            posX = rightEdge;
            posY += (velY != 0 ? velY : -service.dpToPx(2.2f));
            facing = -1;

            if (posY <= topEdge) {
                posY = topEdge;
                state = "CEILING";
                facing = -1;
                velX = -service.dpToPx(2f);
            } else if (posY >= bottomEdge) {
                posY = bottomEdge;
                state = "WALK";
                velX = -service.dpToPx(2f);
            }
        }
        // 6. Caminar por el techo
        else if ("CEILING".equals(state)) {
            posY = topEdge;
            posX += velX;

            if (posX <= leftEdge || posX >= rightEdge || random.nextFloat() < 0.02f) {
                state = "FALL";
                velY = service.dpToPx(1.5f);
            }
        }
        // 7. Danza
        else if ("DANCE".equals(state)) {
            if (tickCount % 6 == 0) {
                facing = -facing;
            }
            stateTimer--;
            if (stateTimer <= 0) pickRandomState();
        }
        // 8. Rodar
        else if ("ROLL".equals(state)) {
            posX += velX;
            if (posX <= leftEdge) {
                posX = leftEdge;
                velX = Math.abs(velX);
                facing = 1;
            } else if (posX >= rightEdge) {
                posX = rightEdge;
                velX = -Math.abs(velX);
                facing = -1;
            }
            stateTimer--;
            if (stateTimer <= 0) pickRandomState();
        }
        // 9. Salto acrobatico
        else if ("JUMP".equals(state)) {
            velY += 1.8f;
            posY += velY;
            posX += velX;

            if (posX <= leftEdge) {
                posX = leftEdge;
                velX = -velX * 0.5f;
            } else if (posX >= rightEdge) {
                posX = rightEdge;
                velX = -velX * 0.5f;
            }

            if (posY >= currentFloorY) {
                posY = currentFloorY;
                velY = 0;
                velX = 0;
                state = "STAND";
                stateTimer = 40 + random.nextInt(50);
                service.triggerHaptic(15);
            }
        }
        // 10. Accion personalizada de la skin
        else if ("CUSTOM_ACTION".equals(state)) {
            stateTimer--;
            if (stateTimer <= 0) pickRandomState();
        }
        // 11. Estados estaticos
        else {
            stateTimer--;
            if (stateTimer <= 0) pickRandomState();
        }

        // Clamp absoluto e inquebrantable a los limites de la pantalla
        posX = Math.max(leftEdge, Math.min(rightEdge, posX));
        posY = Math.max(topEdge, Math.min(bottomEdge, posY));

        int talkIntervalSec = service.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE)
            .getInt("shimeji_talk_interval_sec", 45);
        if (talkIntervalSec > 0) {
            int ticksNeeded = Math.max(100, talkIntervalSec * 25);
            if (random.nextInt(ticksNeeded) == 7 && tvSpeechBubble.getVisibility() != View.VISIBLE && layoutLongPressMenu.getVisibility() != View.VISIBLE) {
                String[] dl = skin.dialogues;
                if (dl.length > 0) {
                    say(dl[random.nextInt(dl.length)], 3500);
                }
            }
        }

        int shakeOffX = 0;
        int shakeOffY = 0;
        if (shakeTicks > 0) {
            shakeTicks--;
            shakeOffX = (random.nextInt(7) - 3) * service.dpToPx(1.5f);
            shakeOffY = (random.nextInt(7) - 3) * service.dpToPx(1.5f);
        }

        params.x = (int) posX + shakeOffX;
        params.y = (int) posY + shakeOffY;
        service.getWindowManager().updateViewLayout(overlayView, params);

        updateSprite();
    }

    private void pickRandomState() {
        if (isKo) return;
        SharedPreferences sp = service.getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE);
        float speedMult = sp.getFloat("shimeji_walk_speed_mult", 1.0f);
        boolean allowSit = sp.getBoolean("allow_sitting", true);
        boolean allowCustom = sp.getBoolean("allow_custom_actions", true);

        float r = random.nextFloat();
        if (r < 0.40f) {
            state = "WALK";
            facing = random.nextBoolean() ? 1 : -1;
            velX = facing * (service.dpToPx(1.5f) + random.nextFloat() * service.dpToPx(1.5f)) * speedMult;
            stateTimer = 90 + random.nextInt(120);
        } else if (r < 0.65f) {
            state = "ROAM";
            facing = random.nextBoolean() ? 1 : -1;
            velX = facing * (service.dpToPx(1.2f) + random.nextFloat() * service.dpToPx(1.5f)) * speedMult;
            velY = (random.nextBoolean() ? 1 : -1) * (service.dpToPx(1f) + random.nextFloat() * service.dpToPx(1.5f)) * speedMult;
            stateTimer = 80 + random.nextInt(100);
        } else if (r < 0.80f) {
            state = "STAND";
            velX = 0;
            velY = 0;
            stateTimer = 60 + random.nextInt(90);
        } else if (r < 0.90f && allowSit) {
            state = "SIT";
            velX = 0;
            velY = 0;
            stateTimer = 80 + random.nextInt(90);
        } else if (allowCustom) {
            String[][] actions = SkinData.getCustomActions(skin.id);
            if (actions != null && actions.length > 0) {
                int chosenAct = random.nextInt(actions.length);
                triggerCustomAction(chosenAct);
            } else {
                state = "STAND";
                stateTimer = 60;
            }
        } else {
            state = "STAND";
            stateTimer = 60;
        }
    }

    public void updateSprite() {
        String frameName = "stand1";

        if ("KO".equals(state) || isKo) {
            frameName = "kneel1";
        } else if ("FLUNG".equals(state) || "FALL".equals(state) || "ROAM".equals(state)) {
            frameName = (Math.abs(velY) > service.dpToPx(3)) ? "fall1" : "stand1";
        } else if ("JUMP".equals(state)) {
            frameName = (velY > 0) ? "fall1" : "stand3";
        } else if ("DANCE".equals(state)) {
            String[] danceFrames = {"walk2", "walk4", "stand2", "sit1"};
            int idx = (tickCount / 4) % danceFrames.length;
            frameName = danceFrames[idx];
        } else if ("ROLL".equals(state)) {
            String[] rollFrames = {"fall1", "sit1", "stand1"};
            int idx = (tickCount / 3) % rollFrames.length;
            frameName = rollFrames[idx];
        } else if ("CEILING".equals(state)) {
            // Dokis usan su sprite dedicado climb_top para escalar el techo
            if (skin.folder.matches("Monika|Sayori|Natsuki|Yuri")) {
                frameName = "climb_top";
            } else {
                String[] walkFrames = {"walk1", "walk2", "walk3", "walk4", "walk5"};
                int idx = (tickCount / 5) % walkFrames.length;
                frameName = walkFrames[idx];
            }
        } else if ("WALK".equals(state)) {
            String[] walkFrames = {"walk1", "walk2", "walk3", "walk4", "walk5"};
            int idx = (tickCount / 5) % walkFrames.length;
            frameName = walkFrames[idx];
        } else if ("CLIMB_LEFT".equals(state) || "CLIMB_RIGHT".equals(state)) {
            String[] climbFrames = {"climb1", "climb2"};
            int idx = (tickCount / 7) % climbFrames.length;
            frameName = climbFrames[idx];
        } else if ("SIT".equals(state)) {
            frameName = "sit1";
        } else if ("CUSTOM_ACTION".equals(state)) {
            if (customFrameName1 != null && customFrameName2 != null) {
                frameName = ((tickCount / 10) % 2 == 0) ? customFrameName1 : customFrameName2;
            } else if (customFrameName1 != null) {
                frameName = customFrameName1;
            } else {
                frameName = "sit1";
            }
        } else if ("GUITAR".equals(state)) {
            String[] guitarFrames = {"guitar1", "guitar2", "guitar3"};
            int idx = (tickCount / 6) % guitarFrames.length;
            frameName = guitarFrames[idx];
        } else if ("BOX".equals(state)) {
            String[] boxFrames = {"box1", "box2", "box3"};
            int idx = (tickCount / 12) % boxFrames.length;
            frameName = boxFrames[idx];
        } else {
            String[] standFrames = {"stand1", "stand2", "stand1", "stand3"};
            int idx = (tickCount / 12) % standFrames.length;
            frameName = standFrames[idx];
        }

        Bitmap bmp = service.loadSkinBitmap(skin.folder, frameName, facing);
        if (bmp != null) {
            ivSprite.setImageBitmap(bmp);
        }
    }

    public void updateSize(int newSizePx) {
        ivSprite.getLayoutParams().width = newSizePx;
        ivSprite.getLayoutParams().height = newSizePx;
        ivSprite.requestLayout();
        service.getWindowManager().updateViewLayout(overlayView, params);
    }

    public void destroy() {
        if (hideBubbleRunnable != null) handler.removeCallbacks(hideBubbleRunnable);
        if (longPressRunnable != null) handler.removeCallbacks(longPressRunnable);
        if (overlayView != null) {
            try {
                service.getWindowManager().removeView(overlayView);
            } catch (Exception ignored) {}
        }
    }
}
