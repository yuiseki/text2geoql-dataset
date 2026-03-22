[out:json][timeout:30];
area["name:en"="Cairo"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;