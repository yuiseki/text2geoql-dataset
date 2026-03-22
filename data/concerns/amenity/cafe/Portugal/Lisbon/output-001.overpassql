[out:json][timeout:30];
area["name:en"="Lisbon"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;