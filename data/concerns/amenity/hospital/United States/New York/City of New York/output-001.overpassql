[out:json][timeout:30];
area["name"="City of New York"]->.searchArea;
(
  nwr["amenity"="hospital"](area.searchArea);
);
out geom;
