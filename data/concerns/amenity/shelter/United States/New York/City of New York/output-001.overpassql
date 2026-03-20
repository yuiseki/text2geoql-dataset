[out:json][timeout:30];
area["name"="City of New York"]->.searchArea;
(
  nwr["amenity"="shelter"](area.searchArea);
  nwr["amenity"="refugee_site"](area.searchArea);
);
out geom;
