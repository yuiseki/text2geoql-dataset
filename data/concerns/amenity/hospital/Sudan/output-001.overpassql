[out:json][timeout:30000];
area["name"="Sudan"]->.searchArea;
(
  nwr["amenity"="hospital"](area.searchArea);
);
out geom;
