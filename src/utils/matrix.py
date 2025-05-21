def matrice_transition_edge(ordered, col_idx, n_col):
    """
    Transition pour les colonnes de bord (première ou dernière).
    ordered : liste linéaire de (status, CNE, power)
    col_idx : index de la colonne à traiter (0 ou n_col-1)
    n_col   : nombre total de colonnes
    """
    col = ordered[col_idx :: n_col]
    n = len(col)
    labs = ['0'] * n
    i = 0
    while i < n:
        status, cne, power = col[i]
        if status == 'L':
            labs[i] = '0'
            i += 1
        else:
            # on collecte le segment de M/H contigus
            segment = []
            while i < n and col[i][0] in ('M', 'H'):
                segment.append((i, col[i]))
                i += 1
            # priorité aux H
            if any(st == 'H' for _, (st, _, _) in segment):
                for idx, (st, _, _) in segment:
                    labs[idx] = '1' if st == 'H' else '0'
            else:
                # pas de H → on choisit le M de puissance max
                if len(segment) > 1:
                    max_p = max(p for _, (_, _, p) in segment)
                    for idx, (_, _, p) in segment:
                        labs[idx] = '1' if p == max_p else '0'
                else:
                    idx, (_, _, _) = segment[0]
                    labs[idx] = '1'
    # on associe chaque signal à son CNE
    return [[labs[k], col[k][1]] for k in range(n)]


def matrice_transition_centrale(ordered, col_idx, n_col, neighbor='left'):
    """
    Transition pour une colonne centrale.
    ordered  : liste linéaire de (status, CNE, power)
    col_idx  : index de la colonne centrale à traiter (1..n_col-2)
    n_col    : nombre total de colonnes
    neighbor : 'left' ou 'right' pour choisir le côté de comparaison
    """
    mid = ordered[col_idx :: n_col]
    if neighbor == 'left':
        nb = ordered[(col_idx - 1) :: n_col]
    elif neighbor == 'right':
        nb = ordered[(col_idx + 1) :: n_col]
    else:
        raise ValueError("neighbor must be 'left' or 'right'")
    
    n = len(mid)
    def get(col, i):
        return col[i][0] if 0 <= i < n else 'L'
    
    result = ['0'] * n
    i = 0
    while i < n:
        status, cne, power = mid[i]
        voisins_nb  = [get(nb, i-1), get(nb, i), get(nb, i+1)]
        voisins_mid = [get(mid, i-1), get(mid, i+1)]
        
        if status == 'H':
            result[i] = '1'
        elif status == 'L':
            result[i] = '0'
        else:  # 'M'
            # bloqué si voisines à gauche/droite sont H ou M
            if 'H' in voisins_nb or 'M' in voisins_nb or 'H' in voisins_mid:
                result[i] = '0'
            else:
                # collecte du segment de M « libres »
                seq = [(i, power)]
                j = i + 1
                while (j < n
                       and mid[j][0] == 'M'
                       and [get(nb, j-1), get(nb, j), get(nb, j+1)] == ['L']*3):
                    seq.append((j, mid[j][2]))
                    j += 1
                # on garde le M de puissance max
                idx_max, _ = max(seq, key=lambda x: x[1])
                for idx, _ in seq:
                    result[idx] = '1' if idx == idx_max else '0'
                i = j - 1
        i += 1

    return [[result[k], mid[k][1]] for k in range(n)]

def matrice_transitions(matrice, n_col=3, n_ligne=None, neighbor='left'):
    """
    Applique les transitions de chaque colonne pour une matrice n_col × n_ligne.
    Si n_ligne n'est pas fourni, il est déduit de la taille de matrice.
    neighbor détermine pour chaque colonne centrale de quel côté
    (gauche/droite) prendre le voisin.
    """
    total = len(matrice)
    if n_ligne is None:
        if total % n_col != 0:
            raise ValueError(f"Impossible de déduire n_ligne : {total} n'est pas multiple de {n_col}")
        n_ligne = total // n_col

    if total != n_col * n_ligne:
        raise ValueError(f"Attendu {n_col*n_ligne} éléments, reçu {total}")

    cols = []
    for j in range(n_col):
        if j == 0:
            cols.append(matrice_transition_edge(matrice, j, n_col))
        elif j == n_col - 1:
            cols.append(matrice_transition_edge(matrice, j, n_col))
        elif j == 1:
            cols.append(matrice_transition_centrale(matrice, j, n_col, neighbor='left'))
        elif j == n_col - 2 and  n_col > 3:
            cols.append(matrice_transition_centrale(matrice, j, n_col, neighbor='right'))
        elif n_col > 4:
            cols.append(matrice_transition_centrale(matrice, j, n_col, neighbor=neighbor))

    lignes = []
    for i in range(n_ligne):
        # pour chaque ligne i, on prend l’élément i dans chaque colonne j
        ligne = [cols[j][i] for j in range(n_col)]
        lignes.append(ligne)

    # 3) on retourne la liste des lignes
    print(lignes)
    return lignes


if __name__ == "__main__":
    # Exemple 3×7
    matrice = [
        ('L','4455',-55), ('L','1647',-44), ('L','78545',-20), ('M','7845',-20), ('M','78453',-24),
        ('L','8464',-25), ('L','7045',-25), ('L','48545',-20), ('L','1112',-21), ('L','11126',-25),
        ('H','6484',-50), ('M','4546',-11), ('L','88545',-20), ('L','1478',-20), ('L','14785',-24),
        ('M','1986',-26), ('L','1245',-23), ('L','98545',-20), ('L','4475',-20), ('M','44757',-27),
        ('L','4643',-22), ('M','4512',-22), ('M','28545',-20), ('H','4010',-20), ('L','40101',-21),
        ('L','4535',-29), ('M','1244',-24), ('L','80545',-20), ('L','1212',-20), ('L','12127',-25),
        ('L','4068',-20), ('M','7805',-27), ('L','72545',-20), ('L','4405',-20), ('L','44054',-27)
    ]
    # Vous pouvez ajuster n_col et n_ligne à volonté :
    matrice_transitions(matrice, n_col=5, neighbor='right')