[out:json][timeout:30];
area["name:en"="Daegu"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;