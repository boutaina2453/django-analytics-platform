from django.shortcuts import render
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io
import base64

# Variable globale pour stocker les données
df_global = None

def home(request):
    return render(request, 'analysis/home.html')

def clean_data(df):
    """Nettoie les colonnes du DataFrame pour résoudre les problèmes de données concaténées."""
    for col in df.columns:
        if df[col].dtype == 'object':
            # Suppression des chaînes concaténées sans espace ou correction des données mal formatées
            df[col] = df[col].str.split(' ').str[0]  # Nettoyage basique pour les colonnes texte
    return df

def upload_file(request):
    global df_global
    if request.method == 'POST':
        file = request.FILES['file']
        try:
            # Lecture du fichier CSV
            df_global = pd.read_csv(file)
            
            # Nettoyage des données après l'importation
            df_global = clean_data(df_global)

            # Aperçu des données
            preview_data = df_global.head().to_html(classes='table table-striped')
            return render(request, 'analysis/preview.html', {'data_preview': preview_data})
        except Exception as e:
            return render(request, 'analysis/home.html', {'error': f"Erreur d'importation : {e}"})
    return render(request, 'analysis/home.html')

def show_statistics(request):
    global df_global

    if df_global is None:
        return render(request, 'analysis/home.html', {'error': 'Aucun fichier n\'a été chargé.'})

    if request.method == 'POST':
        stat_choice = request.POST.get('stat_choice')
        try:
            if stat_choice:
                # Sélection uniquement des colonnes numériques
                numerical_data = df_global.select_dtypes(include='number')

                # Calcul des statistiques selon le choix de l'utilisateur
                if stat_choice == "mean":
                    stat_value = numerical_data.mean()
                elif stat_choice == "std":
                    stat_value = numerical_data.std()
                elif stat_choice == "min":
                    stat_value = numerical_data.min()
                elif stat_choice == "max":
                    stat_value = numerical_data.max()
                elif stat_choice == "count":
                    stat_value = numerical_data.count()
                elif stat_choice == "median":
                    stat_value = numerical_data.median()
                else:
                    raise ValueError("Statistique non supportée")

                # Passer les résultats des statistiques au template
                return render(request, 'analysis/stats.html', {
                    'stat_data': {'statistic': stat_choice, 'value': stat_value.to_dict()}
                })
        except Exception as e:
            return render(request, 'analysis/home.html', {'error': f"Erreur : {e}"})

    return render(request, 'analysis/stats.html')

def show_visualizations(request):
    global df_global

    if df_global is None:
        return render(request, 'analysis/home.html', {'error': 'Aucun fichier n\'a été chargé.'})

    # Obtenir les colonnes numériques
    numerical_columns = df_global.select_dtypes(include='number').columns

    if request.method == 'POST':
        vis_choice = request.POST.get('vis_choice')
        x_axis = request.POST.get('x_axis')
        y_axis = request.POST.get('y_axis')

        try:
            # Visualisation : Histogramme
            if vis_choice == "Histogramme":
                if x_axis and x_axis in numerical_columns:
                    plt.figure(figsize=(10, 6))
                    df_global[x_axis].hist(bins=20, alpha=0.7)
                    plt.title(f"Histogramme de {x_axis}")
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    vis_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    buf.close()
                    return render(request, 'analysis/visualizations.html', {
                        'vis_type': 'Histogramme',
                        'vis_image': vis_base64
                    })
                else:
                    return render(request, 'analysis/visualizations.html', {
                        'error': "Veuillez sélectionner une colonne valide pour l'histogramme."
                    })

            # Visualisation : Scatter Plot
            elif vis_choice == "Scatter Plot":
                if x_axis and y_axis and x_axis in numerical_columns and y_axis in numerical_columns:
                    fig = px.scatter(
                        df_global,
                        x=x_axis,
                        y=y_axis,
                        title=f"Scatter Plot: {x_axis} vs {y_axis}"
                    )
                    scatter_html = fig.to_html(full_html=False)
                    return render(request, 'analysis/visualizations.html', {
                        'vis_type': 'Scatter Plot',
                        'vis_html': scatter_html,
                    })
                else:
                    return render(request, 'analysis/visualizations.html', {
                        'error': "Veuillez sélectionner des colonnes valides pour le Scatter Plot."
                    })

            # Visualisation : KDE Plot
            elif vis_choice == "KDE Plot":
                if x_axis and x_axis in numerical_columns:
                    plt.figure(figsize=(10, 6))
                    sns.kdeplot(df_global[x_axis].dropna())
                    plt.title(f"KDE Plot de {x_axis}")
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    vis_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    buf.close()
                    return render(request, 'analysis/visualizations.html', {
                        'vis_type': 'KDE Plot',
                        'vis_image': vis_base64
                    })
                else:
                    return render(request, 'analysis/visualizations.html', {
                        'error': "Veuillez sélectionner une colonne valide pour le KDE Plot."
                    })

            # Visualisation : Heatmap
            elif vis_choice == "Heatmap":
                if len(numerical_columns) > 1:
                    plt.figure(figsize=(10, 6))
                    sns.heatmap(df_global[numerical_columns].corr(), annot=True, cmap='coolwarm')
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    vis_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    buf.close()
                    return render(request, 'analysis/visualizations.html', {
                        'vis_type': 'Heatmap',
                        'vis_image': vis_base64,
                    })
                else:
                    return render(request, 'analysis/visualizations.html', {
                        'error': 'Pas assez de colonnes numériques pour générer une Heatmap.'
                    })

        except Exception as e:
            return render(request, 'analysis/visualizations.html', {
                'error': f"Erreur de visualisation : {e}"
            })

    # Si c'est une simple requête GET, envoyer le formulaire par défaut
    return render(request, 'analysis/visualizations.html', {
        'choices': ['Histogramme', 'Scatter Plot', 'KDE Plot', 'Heatmap'],
        'columns': numerical_columns,
    })
