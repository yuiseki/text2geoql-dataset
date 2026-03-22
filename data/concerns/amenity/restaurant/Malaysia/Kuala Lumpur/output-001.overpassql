[out:json][timeout:30];
area["name:en"="Kuala Lumpur"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;