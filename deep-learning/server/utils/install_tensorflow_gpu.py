#!/usr/bin/env python3
"""
Script d'installation automatique TensorFlow GPU
===============================================

Ce script détecte votre système d'exploitation et vous guide
dans l'installation optimale de TensorFlow avec support GPU.

Utilisation: python install_tensorflow_gpu.py

Auteur: Mickael Faust
Date: Juin 2025
"""

import sys
import platform
import subprocess
import shutil

def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step_num, description):
    """Affiche une étape numérotée"""
    print(f"\n📋 Étape {step_num}: {description}")

def run_command(cmd, description="", check=True):
    """Exécute une commande avec gestion d'erreur"""
    if description:
        print(f"   Exécution: {description}")

    print(f"   Commande: {cmd}")

    if input("   Continuer? (y/n): ").lower() != 'y':
        print("   ⏭️  Étape ignorée")
        return False

    try:
        result = subprocess.run(cmd, shell=True, check=check)
        print("   ✅ Succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erreur: {e}")
        return False

def check_command_exists(cmd):
    """Vérifie si une commande existe"""
    return shutil.which(cmd) is not None

def detect_system():
    """Détecte le système d'exploitation et la configuration"""
    system_info = {
        'os': platform.system(),
        'arch': platform.machine(),
        'python_version': platform.python_version(),
        'is_wsl': 'Microsoft' in platform.release() if platform.system() == 'Linux' else False,
        'has_conda': check_command_exists('conda'),
        'has_nvidia': check_command_exists('nvidia-smi')
    }
    return system_info

def install_linux(info):
    """Installation pour Linux/Ubuntu"""
    print_header("INSTALLATION LINUX/UBUNTU")

    print_step(1, "Vérification des prérequis")
    if not info['has_nvidia']:
        print("⚠️  nvidia-smi non détecté")
        print("   Installez d'abord les drivers NVIDIA:")
        print("   sudo apt update")
        print("   sudo apt install nvidia-driver-535")  # ou version plus récente
        print("   sudo reboot")
        return False

    print_step(2, "Création de l'environnement virtuel")

    if info['has_conda']:
        print("🐍 Conda détecté - utilisation recommandée")
        run_command("conda create --name tf-gpu python=3.11.10 -y", "Création environnement conda")
        print("\n⚠️  IMPORTANT: Activez l'environnement avec:")
        print("conda activate tf-gpu")
    else:
        print("🐍 Utilisation de venv")
        # run_command("python3 -m venv tf-gpu-env", "Création environnement venv")
        print("\n⚠️  IMPORTANT: Activez l'environnement avec:")
        print("source tf-gpu-env/bin/activate")

    print_step(3, "Installation TensorFlow GPU")
    print("⚠️  Assurez-vous d'avoir activé votre environnement virtuel!")
    run_command("pip install --upgrade pip", "Mise à jour pip")
    run_command("pip install 'tensorflow[and-cuda]'", "Installation TensorFlow GPU")

    return True

def install_windows_wsl(info):
    """Installation pour Windows WSL2"""
    print_header("INSTALLATION WINDOWS WSL2")

    print_step(1, "Vérification WSL2")
    if not info['is_wsl']:
        print("❌ Ce script doit être exécuté dans WSL2")
        print("   1. Installez WSL2: wsl --install -d Ubuntu-24.04")
        print("   2. Installez les drivers NVIDIA pour WSL")
        print("   3. Relancez ce script dans WSL2")
        return False

    print_step(2, "Vérification drivers NVIDIA")
    if not info['has_nvidia']:
        print("❌ nvidia-smi non disponible")
        print("   Installez les drivers NVIDIA pour WSL depuis Windows")
        print("   NE PAS installer CUDA dans WSL2!")
        return False

    print_step(3, "Installation dépendances Python")
    run_command("sudo apt update", "Mise à jour des paquets")
    run_command("sudo apt install python3.11.10-venv python3-pip -y", "Installation Python")

    print_step(4, "Création environnement virtuel")
    run_command("python3 -m venv tf-gpu", "Création environnement")
    print("\n⚠️  IMPORTANT: Activez l'environnement avec:")
    print("source tf-gpu/bin/activate")

    print_step(5, "Installation TensorFlow GPU")
    print("⚠️  Assurez-vous d'avoir activé votre environnement virtuel!")
    run_command("pip install --upgrade pip", "Mise à jour pip")
    run_command("pip install 'tensorflow[and-cuda]'", "Installation TensorFlow GPU")

    return True

def install_windows_native(info):
    """Installation pour Windows natif (limitée)"""
    print_header("INSTALLATION WINDOWS NATIF")

    print("⚠️  ATTENTION: Support GPU limité à TensorFlow ≤2.10")
    print("   Recommandation: Utilisez WSL2 pour les versions récentes")

    if input("\nContinuer avec Windows natif? (y/n): ").lower() != 'y':
        return False

    print_step(1, "Vérification Conda")
    if not info['has_conda']:
        print("❌ Conda requis pour Windows natif")
        print("   Installez Miniconda: https://docs.conda.io/en/latest/miniconda.html")
        return False

    print_step(2, "Création environnement avec CUDA")
    run_command("conda create --name tf-gpu python=3.10 -y", "Création environnement")
    print("\n⚠️  Activez l'environnement: conda activate tf-gpu")

    print_step(3, "Installation CUDA/cuDNN via Conda")
    run_command("conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0 -y", 
                "Installation CUDA/cuDNN")

    print_step(4, "Installation TensorFlow (version limitée)")
    run_command('pip install "tensorflow<2.11"', "Installation TensorFlow ≤2.10")

    return True

def install_macos(info):
    """Installation pour macOS"""
    print_header("INSTALLATION MACOS")

    # Détecter le type de Mac
    is_apple_silicon = info['arch'].startswith('arm')

    if is_apple_silicon:
        print("🍎 Mac Apple Silicon (M1/M2/M3) détecté")
        print_step(1, "Installation TensorFlow optimisé Apple")

        if info['has_conda']:
            print("Utilisation de Conda (recommandé pour Apple Silicon)")
            run_command("conda create --name tf-metal python=3.11 -y", "Création environnement")
            print("\n⚠️  Activez: conda activate tf-metal")
        else:
            run_command("python3 -m venv tf-metal", "Création environnement venv")
            print("\n⚠️  Activez: source tf-metal/bin/activate")

        print_step(2, "Installation TensorFlow avec Metal")
        run_command("pip install --upgrade pip", "Mise à jour pip")
        run_command("pip install tensorflow-macos", "Installation TensorFlow macOS")
        run_command("pip install tensorflow-metal", "Installation support Metal GPU")

    else:
        print("🍎 Mac Intel détecté")
        print("ℹ️  Support GPU non disponible - installation CPU uniquement")

        print_step(1, "Création environnement")
        run_command("python3 -m venv tf-cpu", "Création environnement")
        print("\n⚠️  Activez: source tf-cpu/bin/activate")

        print_step(2, "Installation TensorFlow CPU")
        run_command("pip install --upgrade pip", "Mise à jour pip")
        run_command("pip install tensorflow", "Installation TensorFlow CPU")

    return True

def main():
    print("🚀 Installation automatique TensorFlow GPU")
    print("Guide d'installation TensorFlow GPU - Juin 2025")

    # Détection système
    info = detect_system()

    print_header("DÉTECTION SYSTÈME")
    print(f"Système d'exploitation: {info['os']}")
    print(f"Architecture: {info['arch']}")
    print(f"Version Python: {info['python_version']}")
    print(f"WSL détecté: {info['is_wsl']}")
    print(f"Conda disponible: {info['has_conda']}")
    print(f"NVIDIA GPU détecté: {info['has_nvidia']}")

    # Vérification version Python
    if not (3, 9) <= tuple(map(int, info['python_version'].split('.')[:2])) <= (3, 12):
        print(f"\n⚠️  Python {info['python_version']} non supporté")
        print("   TensorFlow 2.17+ requiert Python 3.9-3.12")
        return False

    # Choix de la méthode d'installation
    success = False

    if info['os'] == 'Linux':
        if info['is_wsl']:
            success = install_windows_wsl(info)
        else:
            success = install_linux(info)

    elif info['os'] == 'Windows':
        print("\n🪟 Windows détecté")
        print("Méthodes disponibles:")
        print("1. WSL2 (recommandé) - Versions récentes TensorFlow")
        print("2. Natif Windows - Limité à TensorFlow ≤2.10")

        choice = input("\nChoisissez (1/2): ")
        if choice == '1':
            print("\nPour WSL2, exécutez ce script dans Ubuntu WSL")
            print("Installation WSL2: wsl --install -d Ubuntu-24.04")
            return False
        else:
            success = install_windows_native(info)

    elif info['os'] == 'Darwin':  # macOS
        success = install_macos(info)

    else:
        print(f"\n❌ Système non supporté: {info['os']}")
        return False

    # Instructions finales
    if success:
        print_header("INSTALLATION TERMINÉE")
        print("🎉 Installation terminée avec succès!")

        print("\n📋 Prochaines étapes:")
        print("1. Activez votre environnement virtuel")
        print("2. Testez l'installation: python test_tensorflow_gpu.py")
        print("3. Consultez le guide complet: tensorflow-gpu-setup.md")

        print("\n🔍 Commandes de vérification:")
        print("python -c \"import tensorflow as tf; print(tf.__version__)\"")
        print("python -c \"import tensorflow as tf; print(len(tf.config.list_physical_devices('GPU')))\"")

        print("\n📚 Ressources:")
        print("- Documentation TensorFlow: https://www.tensorflow.org/guide/gpu")
        print("- Guide de compatibilité: https://www.tensorflow.org/install/source#gpu")

    else:
        print_header("INSTALLATION ÉCHOUÉE")
        print("❌ L'installation a échoué ou a été interrompue")
        print("\n🔧 Solutions:")
        print("- Consultez le guide manuel: tensorflow-gpu-setup.md")
        print("- Vérifiez les prérequis système")
        print("- Consultez le guide de dépannage")

    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Installation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Erreur inattendue: {e}")
        sys.exit(1)
