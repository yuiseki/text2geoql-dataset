[out:json][timeout:30];
area["name:en"="Incheon"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;