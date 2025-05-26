# =============================
#  League of Legends OLAP Analysis
# =============================

import pandas as pd
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
import os

# Create 'plots' folder if it doesn't exist
plot_dir = '/content/plots'
os.makedirs(plot_dir, exist_ok=True)


# -------------------
# Load Data
# -------------------
# Upload the CSV or mount from drive
# Example: df = pd.read_csv('/content/your_file.csv')
df = pd.read_csv('/content/lol_ranked_games.csv')  # update path if needed

# -------------------
# 1. Gold Diff vs Win Rate
# -------------------
df['gold_bucket'] = pd.cut(
    df['goldDiff'],
    bins=[-10000, -5000, -2000, 0, 2000, 5000, 10000],
    labels=['<<-5k', '-5k to -2k', '-2k to 0', '0 to +2k', '+2k to +5k', '>>+5k']
)
win_rates = df.groupby('gold_bucket')['hasWon'].mean()


plt.figure(figsize=(8, 5))
win_rates.plot(kind='bar', color='skyblue')
plt.title("Win Rate by Gold Difference")
plt.xlabel("Gold Difference Buckets")
plt.ylabel("Win Rate")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{plot_dir}/win_rate_by_gold_diff.pdf", format='pdf')
plt.show()

# -------------------
# 2. Game Duration Distribution
# -------------------
plt.figure(figsize=(10, 5))
df[df['hasWon'] == 1]['gameDuration'].plot(kind='hist', bins=30, alpha=0.6, label='Win', color='green')
df[df['hasWon'] == 0]['gameDuration'].plot(kind='hist', bins=30, alpha=0.6, label='Loss', color='red')
plt.legend()
plt.title("Game Duration Distribution (Win vs Loss)")
plt.xlabel("Game Duration (seconds)")
plt.ylabel("Frequency")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{plot_dir}/game_duration_distribution.pdf", format='pdf')
plt.show()

# -------------------
# 3. Objectives vs Win Rate
# -------------------
objectives = ['killedFireDrake', 'killedBaronNashor', 'killedRiftHerald', 'destroyedTopInhibitor']
avg_obj = df.groupby('hasWon')[objectives].mean().T

plt.figure(figsize=(10, 6))
avg_obj.plot(kind='bar')
plt.title("Average Objectives per Game (Win vs Loss)")
plt.ylabel("Average Count")
plt.xlabel("Objective")
plt.legend(['Loss', 'Win'])
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{plot_dir}/avg_obj_per_game.pdf", format='pdf')
plt.show()

# -------------------
# 4. KDA Distributions
# -------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for ax, stat in zip(axes, ['kills', 'deaths', 'assists']):
    df.boxplot(column=stat, by='hasWon', ax=ax)
    ax.set_title(f"{stat.capitalize()} by Win/Loss")
    ax.set_xlabel("Has Won")
    ax.set_ylabel(stat.capitalize())

plt.suptitle("KDA Distributions by Outcome")
plt.tight_layout()
plt.savefig(f"{plot_dir}/KDA_dist.pdf", format='pdf')
plt.show()

# -------------------
# 5. First Blood & First Tower
# -------------------
early_events = df.groupby(['isFirstBlood', 'isFirstTower'])['hasWon'].mean().unstack()

plt.figure(figsize=(8, 5))
early_events.plot(kind='bar', colormap='coolwarm')
plt.title("Win Rate by First Blood and Tower")
plt.ylabel("Win Rate")
plt.xlabel("First Blood")
plt.xticks([0, 1], ['No', 'Yes'], rotation=0)
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{plot_dir}/Win_rate_FB.pdf", format='pdf')
plt.show()

# -------------------
# 6. Wards Placed vs Win Rate
# -------------------
df['wards_bucket'] = pd.cut(df['wardsPlaced'], bins=10)
vision_win_rate = df.groupby('wards_bucket')['hasWon'].mean()

plt.figure(figsize=(10, 5))
vision_win_rate.plot(kind='line', marker='o')
plt.title("Win Rate by Wards Placed")
plt.xlabel("Wards Placed (Binned)")
plt.ylabel("Win Rate")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{plot_dir}/wards_vs_wins.pdf", format='pdf')
plt.show()

# -------------------
# 7. Kill Participation
# -------------------
df['kill_participation'] = (df['assists'] + df['kills']) / (df['kills'] + df['deaths'] + 1e-6)
df['kill_participation'] = df['kill_participation'].clip(0, 2)

plt.figure(figsize=(10, 5))
plt.hist(df[df['hasWon'] == 1]['kill_participation'], bins=30, alpha=0.5, label='Win')
plt.hist(df[df['hasWon'] == 0]['kill_participation'], bins=30, alpha=0.5, label='Loss')
plt.title("Kill Participation by Outcome")
plt.xlabel("Kill Participation Ratio")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig(f"{plot_dir}/kill_participation.pdf", format='pdf')
plt.show()

fig, ax = plt.subplots(1, 2, figsize=(14, 5))

# First Tower
tower_win = df.groupby('isFirstTower')['hasWon'].mean()
ax[0].bar(['No First Tower', 'Got First Tower'], tower_win, color=['gray', 'green'])
ax[0].set_title('Win Rate vs First Tower')
ax[0].set_ylabel('Win Rate')
ax[0].set_ylim(0, 1)

# First Blood
blood_win = df.groupby('isFirstBlood')['hasWon'].mean()
ax[1].bar(['No First Blood', 'Got First Blood'], blood_win, color=['gray', 'red'])
ax[1].set_title('Win Rate vs First Blood')
ax[1].set_ylim(0, 1)

plt.tight_layout()
plt.savefig(f"{plot_dir}/first_tower_blood.pdf", format='pdf')
plt.show()

dragon_cols = ['killedFireDrake', 'killedWaterDrake', 'killedAirDrake', 
               'killedEarthDrake', 'killedElderDrake']

dragon_win_rates = {
    dragon: df[df[dragon] > 0]['hasWon'].mean() for dragon in dragon_cols
}

plt.figure(figsize=(8, 5))
plt.bar(dragon_win_rates.keys(), dragon_win_rates.values(), color='orange')
plt.title('Win Rate vs Dragon Type Taken')
plt.ylabel('Win Rate')
plt.ylim(0, 1)
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--')
plt.savefig(f"{plot_dir}/win_vs_dragon", format='pdf')
plt.show()

df['kda'] = (df['kills'] + df['assists']) / df['deaths'].replace(0, 1)  # Avoid div by 0
df['kda_bucket'] = pd.cut(df['kda'], bins=[-1, 1, 2, 3, 4, 5, 10, 20], 
                          labels=['<1', '1-2', '2-3', '3-4', '4-5', '5-10', '10+'])

kda_win = df.groupby('kda_bucket')['hasWon'].mean()

plt.figure(figsize=(8, 5))
kda_win.plot(kind='bar', color='purple')
plt.title('Win Rate vs KDA Bucket')
plt.ylabel('Win Rate')
plt.xlabel('KDA')
plt.ylim(0, 1)
plt.grid(axis='y')
plt.savefig(f"{plot_dir}/win_vs_KDA.pdf", format='pdf')
plt.show()

plt.figure(figsize=(8, 5))
plt.hist(df['gameDuration'] / 60, bins=20, color='steelblue', edgecolor='black')
plt.title('Distribution of Game Durations')
plt.xlabel('Game Duration (minutes)')
plt.ylabel('Number of Games')
plt.grid(axis='y')
plt.savefig(f"{plot_dir}/distibution_durations", format='pdf')
plt.show()

df['wards_bucket'] = pd.cut(df['wardsPlaced'], bins=[-1, 5, 10, 15, 20, 30, 50, 100], 
                            labels=['0-5', '6-10', '11-15', '16-20', '21-30', '31-50', '51+'])
ward_win = df.groupby('wards_bucket')['hasWon'].mean()

plt.figure(figsize=(8, 5))
ward_win.plot(kind='bar', color='olive')
plt.title('Win Rate vs Wards Placed')
plt.ylabel('Win Rate')
plt.xlabel('Wards Placed Bucket')
plt.ylim(0, 1)
plt.grid(axis='y')
plt.savefig(f"{plot_dir}/win_vs_wards.pdf", format='pdf')
plt.show()



pivot_kda_vision = pd.pivot_table(df, values='hasWon', index='kda_bucket', columns='wards_bucket')

plt.figure(figsize=(10, 6))
sns.heatmap(pivot_kda_vision, annot=True, fmt='.2f', cmap='YlGnBu')
plt.title("Pivot: Win Rate by KDA and Vision")
plt.ylabel("KDA Bucket")
plt.xlabel("Wards Placed Bucket")
plt.tight_layout()
plt.savefig(f"{plot_dir}/wis_vs_KDA_Vision.pdf", format='pdf')
plt.show()

# ====================
# Additional Analysis Enhancements
# ====================

import numpy as np

# 1. EXP Diff vs Win Rate
df['exp_bucket'] = pd.cut(
    df['expDiff'],
    bins=[-10000, -5000, -2000, 0, 2000, 5000, 10000],
    labels=['<<-5k', '-5k to -2k', '-2k to 0', '0 to +2k', '+2k to +5k', '>>+5k']
)
exp_win_rates = df.groupby('exp_bucket')['hasWon'].mean()

plt.figure(figsize=(8,5))
exp_win_rates.plot(kind='bar', color='teal')
plt.title("Win Rate by Experience Difference")
plt.xlabel("Experience Difference Buckets")
plt.ylabel("Win Rate")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{plot_dir}/win_vs_experiance.pdf", format='pdf')
plt.show()


# 2. Champion Level Difference Impact
plt.figure(figsize=(8,5))
sns.boxplot(x='hasWon', y='champLevelDiff', data=df, palette=['red', 'green'])
plt.title("Champion Level Difference Distribution by Win/Loss")
plt.xlabel("Has Won")
plt.ylabel("Champion Level Difference")
plt.tight_layout()
plt.savefig(f"{plot_dir}/champions_level_diff.pdf", format='pdf')
plt.show()


# 3. Impact of Losing Objectives on Win Rate (e.g. lostBaronNashor, lostElderDrake)
lost_obj_cols = ['lostFireDrake', 'lostWaterDrake', 'lostAirDrake', 'lostEarthDrake', 'lostElderDrake', 'lostBaronNashor']
lost_obj_winrate = df.groupby('hasWon')[lost_obj_cols].mean().T

plt.figure(figsize=(10,6))
lost_obj_winrate.plot(kind='bar', stacked=False)
plt.title("Average Lost Objectives per Game (Win vs Loss)")
plt.ylabel("Average Count")
plt.xlabel("Lost Objective")
plt.legend(['Loss', 'Win'])
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{plot_dir}/avg_lost_obj.pdf", format='pdf')
plt.show()


# 4. Turret Destruction Impact: Total Turrets Destroyed vs Win Rate
df['total_turrets_destroyed'] = (
    df[['destroyedTopNexusTurret', 'destroyedMidNexusTurret', 'destroyedBotNexusTurret',
        'destroyedTopBaseTurret', 'destroyedMidBaseTurret', 'destroyedBotBaseTurret',
        'destroyedTopInnerTurret', 'destroyedMidInnerTurret', 'destroyedBotInnerTurret',
        'destroyedTopOuterTurret', 'destroyedMidOuterTurret', 'destroyedBotOuterTurret']].sum(axis=1)
)

turret_bins = [0, 1, 3, 5, 8, 12]
df['turret_bucket'] = pd.cut(df['total_turrets_destroyed'], bins=turret_bins, labels=['1', '2-3', '4-5', '6-8', '9-12'])
turret_win_rate = df.groupby('turret_bucket')['hasWon'].mean()

plt.figure(figsize=(8,5))
turret_win_rate.plot(kind='bar', color='coral')
plt.title("Win Rate by Number of Turrets Destroyed")
plt.xlabel("Turrets Destroyed")
plt.ylabel("Win Rate")
plt.ylim(0,1)
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{plot_dir}/win_vs_turrets.pdf", format='pdf')
plt.show()


# 5. Deaths vs Win Rate (Binned)
df['deaths_bucket'] = pd.cut(df['deaths'], bins=[-1, 1, 3, 5, 10, 20], labels=['0-1', '2-3', '4-5', '6-10', '10+'])
death_win_rate = df.groupby('deaths_bucket')['hasWon'].mean()

plt.figure(figsize=(8,5))
death_win_rate.plot(kind='bar', color='brown')
plt.title("Win Rate by Death Count Bucket")
plt.xlabel("Deaths")
plt.ylabel("Win Rate")
plt.ylim(0,1)
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{plot_dir}/win_rate_death_count.pdf", format='pdf')
plt.show()


# 6. Correlation Heatmap (Numerical Features Only)
numerical_cols = ['gameDuration', 'goldDiff', 'expDiff', 'champLevelDiff', 'kills', 'deaths', 'assists',
                  'wardsPlaced', 'wardsDestroyed', 'wardsLost', 'kill_participation', 'kda', 'total_turrets_destroyed']

plt.figure(figsize=(12,10))
corr = df[numerical_cols + ['hasWon']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', square=True, cbar_kws={'shrink':.8})
plt.title("Correlation Heatmap of Key Features")
plt.tight_layout()
plt.savefig(f"{plot_dir}/correlation.pdf", format='pdf')
plt.show()


# 7. Impact of Lost Inhibitors on Win Rate
lost_inhib_cols = ['lostTopInhibitor', 'lostMidInhibitor', 'lostBotInhibitor']
lost_inhib_winrate = df.groupby('hasWon')[lost_inhib_cols].mean().T

plt.figure(figsize=(8,5))
lost_inhib_winrate.plot(kind='bar', stacked=False)
plt.title("Average Lost Inhibitors per Game (Win vs Loss)")
plt.xlabel("Lost Inhibitor")
plt.ylabel("Average Count")
plt.legend(['Loss', 'Win'])
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{plot_dir}/Lost_inhibitors.pdf", format='pdf')
plt.show()


# 8. Assist to Death Ratio Distribution by Win/Loss
df['assist_death_ratio'] = df['assists'] / df['deaths'].replace(0,1)

plt.figure(figsize=(10,5))
sns.kdeplot(data=df[df['hasWon']==1], x='assist_death_ratio', label='Win', fill=True, color='green', alpha=0.5)
sns.kdeplot(data=df[df['hasWon']==0], x='assist_death_ratio', label='Loss', fill=True, color='red', alpha=0.5)
plt.title("Assist to Death Ratio Density by Outcome")
plt.xlabel("Assist/Death Ratio")
plt.xlim(0, 10)
plt.legend()
plt.tight_layout()
plt.savefig(f"{plot_dir}/AD_ratio.pdf", format='pdf')
plt.show()

