[out:json][timeout:30];
area["name:en"="Daegu"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;