[out:json][timeout:30000];
area["name"="City of New York"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;
