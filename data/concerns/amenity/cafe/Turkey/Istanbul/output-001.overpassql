[out:json][timeout:30];
area["name:en"="Istanbul"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;