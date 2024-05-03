[out:json][timeout:30000];
area["name"="City of New York"]->.searchArea;
(
  nwr["amenity"="bar"](area.searchArea);
);
out geom;
