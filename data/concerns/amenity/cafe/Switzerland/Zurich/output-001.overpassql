[out:json][timeout:30];
area["name:en"="Zurich"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;