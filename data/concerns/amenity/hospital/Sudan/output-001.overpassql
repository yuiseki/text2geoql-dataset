[out:json][timeout:30];
area["name"="Sudan"]->.searchArea;
(
  nwr["amenity"="hospital"](area.searchArea);
);
out geom;
