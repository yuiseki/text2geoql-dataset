[out:json][timeout:30000];
area["name:en"="Municipality of Prizren"]->.searchArea;
(
  nwr["amenity"="bar"](area.searchArea);
);
out geom;
