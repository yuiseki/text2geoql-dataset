[out:json][timeout:30000];
area["name:en"="Sudan"]->.searchArea;
(
  nwr["amenity"="shelter"](area.searchArea);
  nwr["amenity"="refugee_site"](area.searchArea);
);
out geom;
