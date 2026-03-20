[out:json][timeout:30];
area["name"="City of New York"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;
