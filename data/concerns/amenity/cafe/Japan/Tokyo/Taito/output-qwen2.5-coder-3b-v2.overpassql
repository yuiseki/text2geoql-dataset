[out:json][timeout:30];
area(id:3601758888)->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;
