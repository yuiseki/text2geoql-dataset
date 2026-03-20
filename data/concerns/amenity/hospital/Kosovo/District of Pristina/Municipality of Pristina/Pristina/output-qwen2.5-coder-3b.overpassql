[out:json][timeout:30];
area["name:en"="Pristina"]->.searchArea;
(
  nwr["amenity"="hospital"](area.searchArea);
);
out geom;
