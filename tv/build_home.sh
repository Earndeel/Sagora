#!/bin/sh
# Lanceur « Paysages » du dongle TV (local.codex.depthhome), reconstruit depuis les sources de Codex.
# 1.4 : AIOStreams en première tuile. 1.5 : l'appli s'appelle Sagora ; 1.6 : la tuile ouvre l'appli Sagora (cloud.walter.sagora) (2026-11-05) — la première tuile
# montre la vignette Sagora (assets/sagora_banner.png, générée par front/brand/make.py sur la VM) et ouvre AIOStreams.
set -e
C=~/Documents/Codex/2026-10-26/t-as-acces-a-quel-appareil/work
B=~/walter-tv/depth-home-build
rm -rf "$B"; mkdir -p "$B"
cp -R "$C/depth-home" "$B/depth-home"
ln -s "$C/android-tools" "$B/android-tools"; ln -s "$C/java-runtime" "$B/java-runtime"; ln -s "$C/depth-home-signing.p12" "$B/depth-home-signing.p12"
sed -e "s/'--version-code', '4', '--version-name', '1.3-stable'/'--version-code', '7', '--version-name', '1.6-sagora'/" "$C/build_depth_home.py" > "$B/build_depth_home.py"
cp ~/walter-tv/sagora-banner.png "$B/depth-home/assets/sagora_banner.png"
F="$B/depth-home/src/local/codex/depthhome/MainActivity.java"
sed -i '' -e 's/{"Stremio", "YouTube", "Play Store"}/{"Sagora", "YouTube", "Play Store"}/' \
          -e 's/{"com.stremio.one", "io.gh.reisxd.tizentube.cobalt", "com.android.vending"}/{"cloud.walter.sagora", "io.gh.reisxd.tizentube.cobalt", "com.android.vending"}/' "$F"
python3 - "$F" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
old = """                if (banners[i] == null) banners[i] = pm.getApplicationIcon(info);
            } catch (Exception ignored) { }
        }
    }"""
new = """                if (banners[i] == null) banners[i] = pm.getApplicationIcon(info);
            } catch (Exception ignored) { }
        }
        // Sagora : sa propre vignette plutôt que l'icône de l'appli AIOStreams qu'elle ouvre.
        try (java.io.InputStream in = getAssets().open("sagora_banner.png")) {
            Bitmap sagora = BitmapFactory.decodeStream(in);
            if (sagora != null) banners[0] = new android.graphics.drawable.BitmapDrawable(getResources(), sagora);
        } catch (Exception ignored) { }
    }"""
assert s.count(old) == 1, "loadBanners introuvable"
open(p, "w").write(s.replace(old, new))
PY
grep -n -E "LABELS =|PACKAGES =|sagora_banner" "$F"
grep -c "1.6-sagora" "$B/build_depth_home.py"
cd "$B" && python3 build_depth_home.py
