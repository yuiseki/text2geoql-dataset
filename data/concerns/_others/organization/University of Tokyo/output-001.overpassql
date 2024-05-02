[out:json][timeout:30000];
area["name:en"="Tokyo"]->.searchArea;
(
  nwr["name"~"University of Tokyo"]["amenity"="university"](area.searchArea);
  nwr["name:en"~"University of Tokyo"]["amenity"="university"](area.searchArea);
);
out geom;
