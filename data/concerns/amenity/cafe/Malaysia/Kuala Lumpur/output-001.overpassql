[out:json][timeout:30];
area["name:en"="Kuala Lumpur"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;