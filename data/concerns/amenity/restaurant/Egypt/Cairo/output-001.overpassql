[out:json][timeout:30];
area["name:en"="Cairo"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;