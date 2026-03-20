[out:json][timeout:30];
area["name"~"Kanazawa|Wakayama"]->.searchArea;
(
  nwr["amenity"="fast_food"]["cuisine"="burger"](area.searchArea);
);
out geom;
