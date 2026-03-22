[out:json][timeout:30];
area["name:en"="Istanbul"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;