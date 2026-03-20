[out:json][timeout:30];
area["name:en"="Tokyo"]->.searchArea;
(
  nwr["amenity"="university"](area.searchArea);
);
out geom;
